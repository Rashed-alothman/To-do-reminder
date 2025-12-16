import requests
import sys

BASE_URL = 'http://localhost:5000/homepage/api/tasks'

# Color codes for terminal output (optional, works on most terminals)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test_header(test_num, description):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}[TEST {test_num}] {description}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}→ {message}{RESET}")

# Test counters
passed = 0
failed = 0
task_ids = []

print(f"\n{BLUE}{'='*70}")
print(f"TMS (Task Management System) - Complete API Test Suite")
print(f"{'='*70}{RESET}\n")

# ============================================================================
# TEST 1: Add Multiple Tasks
# ============================================================================
print_test_header(1, "Creating Multiple Tasks")
try:
    for i in range(1, 4):
        response = requests.post(
            f'{BASE_URL}/add_Tasks',
            json={'description': f'Task {i}'}
        )
        if response.status_code == 201:
            result = response.json()
            task_id = result['task']['id']
            task_ids.append(task_id)
            print_success(f"Created task with ID: {task_id}")
            print_info(f"Description: {result['task']['description']}")
            passed += 1
        else:
            print_error(f"Failed to create task {i}: {response.status_code}")
            failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 2: Verify All Tasks Created
# ============================================================================
print_test_header(2, "Retrieving All Tasks")
try:
    response = requests.get(f'{BASE_URL}')
    if response.status_code == 200:
        all_tasks = response.json().get('Tasks', [])
        print_success(f"Retrieved {len(all_tasks)} tasks")
        for task in all_tasks:
            status = "✓ Done" if task.get('completed') else "○ Pending"
            print_info(f"{status} ID: {task['id'][:8]}... | {task['description']}")
        passed += 1
    else:
        print_error(f"Failed to retrieve tasks: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 3: Update Task Description
# ============================================================================
print_test_header(3, "Updating Task Description")
if task_ids:
    try:
        update_id = task_ids[0]
        response = requests.patch(
            f'{BASE_URL}/updatedtask',
            json={
                'id': update_id,
                'description': 'Updated: Buy groceries and cook dinner'
            }
        )
        if response.status_code == 200:
            result = response.json()
            print_success(f"Updated task {update_id[:8]}...")
            print_info(f"New description: {result['task']['description']}")
            passed += 1
        else:
            print_error(f"Update failed: {response.status_code} - {response.json()}")
            failed += 1
    except Exception as e:
        print_error(f"Exception occurred: {e}")
        failed += 1
else:
    print_error("No tasks available to update")
    failed += 1

# ============================================================================
# TEST 4: Mark Task as Completed
# ============================================================================
print_test_header(4, "Marking Task as Completed")
if len(task_ids) > 1:
    try:
        complete_id = task_ids[1]
        response = requests.patch(
            f'{BASE_URL}/updatedtask',
            json={
                'id': complete_id,
                'completed': True
            }
        )
        if response.status_code == 200:
            result = response.json()
            print_success(f"Marked task {complete_id[:8]}... as completed")
            print_info(f"Completed status: {result['task']['completed']}")
            passed += 1
        else:
            print_error(f"Failed to mark complete: {response.status_code}")
            failed += 1
    except Exception as e:
        print_error(f"Exception occurred: {e}")
        failed += 1
else:
    print_error("Not enough tasks to test completion")
    failed += 1

# ============================================================================
# TEST 5: Update Both Description and Status
# ============================================================================
print_test_header(5, "Updating Description AND Completion Status")
if len(task_ids) > 2:
    try:
        update_id = task_ids[2]
        response = requests.patch(
            f'{BASE_URL}/updatedtask',
            json={
                'id': update_id,
                'description': 'Completely updated task',
                'completed': True
            }
        )
        if response.status_code == 200:
            result = response.json()
            print_success(f"Updated task {update_id[:8]}... fully")
            print_info(f"Description: {result['task']['description']}")
            print_info(f"Completed: {result['task']['completed']}")
            passed += 1
        else:
            print_error(f"Failed: {response.status_code}")
            failed += 1
    except Exception as e:
        print_error(f"Exception occurred: {e}")
        failed += 1
else:
    print_error("Not enough tasks for this test")
    failed += 1

# ============================================================================
# TEST 6: View Updated Tasks
# ============================================================================
print_test_header(6, "Verifying Updates")
try:
    response = requests.get(f'{BASE_URL}')
    if response.status_code == 200:
        all_tasks = response.json().get('Tasks', [])
        print_success(f"Retrieved {len(all_tasks)} tasks after updates")
        for task in all_tasks:
            status = "✓ Done" if task.get('completed') else "○ Pending"
            print_info(f"{status} ID: {task['id'][:8]}... | {task['description']}")
        passed += 1
    else:
        print_error(f"Failed to retrieve: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 7: Delete a Task
# ============================================================================
print_test_header(7, "Deleting a Task")
if task_ids:
    try:
        delete_id = task_ids[0]
        response = requests.delete(
            f'{BASE_URL}/delete_task',
            json={'id': delete_id}
        )
        if response.status_code == 200:
            print_success(f"Deleted task {delete_id[:8]}...")
            print_info(f"Response: {response.json().get('message')}")
            passed += 1
        else:
            print_error(f"Delete failed: {response.status_code}")
            failed += 1
    except Exception as e:
        print_error(f"Exception occurred: {e}")
        failed += 1
else:
    print_error("No tasks to delete")
    failed += 1

# ============================================================================
# TEST 8: Try to Update Non-Existent Task (Should Fail)
# ============================================================================
print_test_header(8, "Error Handling: Update Non-Existent Task")
try:
    response = requests.patch(
        f'{BASE_URL}/updatedtask',
        json={
            'id': 'nonexistent-uuid-1234',
            'description': 'This should fail'
        }
    )
    if response.status_code == 404:
        print_success("Correctly returned 404 for non-existent task")
        print_info(f"Response: {response.json()}")
        passed += 1
    else:
        print_error(f"Wrong status code: {response.status_code} (expected 404)")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 9: Try to Update Without ID (Should Fail)
# ============================================================================
print_test_header(9, "Error Handling: Update Without ID")
try:
    response = requests.patch(
        f'{BASE_URL}/updatedtask',
        json={'description': 'No ID provided'}
    )
    if response.status_code == 400:
        print_success("Correctly returned 400 for missing ID")
        print_info(f"Response: {response.json()}")
        passed += 1
    else:
        print_error(f"Wrong status code: {response.status_code} (expected 400)")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 10: Try to Delete Non-Existent Task (Should Fail)
# ============================================================================
print_test_header(10, "Error Handling: Delete Non-Existent Task")
try:
    response = requests.delete(
        f'{BASE_URL}/delete_task',
        json={'id': 'fake-uuid-9999'}
    )
    if response.status_code == 404:
        print_success("Correctly returned 404 for non-existent task")
        print_info(f"Response: {response.json()}")
        passed += 1
    else:
        print_error(f"Wrong status code: {response.status_code} (expected 404)")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 11: Try to Delete Without ID (Should Fail)
# ============================================================================
print_test_header(11, "Error Handling: Delete Without ID")
try:
    response = requests.delete(
        f'{BASE_URL}/delete_task',
        json={'something': 'else'}
    )
    if response.status_code == 400:
        print_success("Correctly returned 400 for missing ID")
        print_info(f"Response: {response.json()}")
        passed += 1
    else:
        print_error(f"Wrong status code: {response.status_code} (expected 400)")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# TEST 12: Try to Add Task Without Description (Should Fail)
# ============================================================================
print_test_header(12, "Error Handling: Add Task Without Description")
try:
    response = requests.post(
        f'{BASE_URL}/add_Tasks',
        json={'title': 'Wrong field'}
    )
    if response.status_code == 400:
        print_success("Correctly returned 400 for missing description")
        print_info(f"Response: {response.json()}")
        passed += 1
    else:
        print_error(f"Wrong status code: {response.status_code} (expected 400)")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# FINAL STATE
# ============================================================================
print_test_header("FINAL", "Remaining Tasks in System")
try:
    response = requests.get(f'{BASE_URL}')
    if response.status_code == 200:
        remaining = response.json().get('Tasks', [])
        if remaining:
            print_info(f"Total remaining: {len(remaining)} tasks")
            for task in remaining:
                status = "✓ Done" if task.get('completed') else "○ Pending"
                print_info(f"{status} ID: {task['id'][:8]}... | {task['description']}")
        else:
            print_info("No tasks remaining in system")
    else:
        print_error(f"Failed to get final state: {response.status_code}")
except Exception as e:
    print_error(f"Exception occurred: {e}")

# ============================================================================
# TEST SUMMARY
# ============================================================================
print(f"\n{BLUE}{'='*70}")
print(f"TEST SUMMARY")
print(f"{'='*70}{RESET}")
print(f"{GREEN}Passed: {passed}{RESET}")
print(f"{RED}Failed: {failed}{RESET}")
print(f"Total:  {passed + failed}")

if failed == 0:
    print(f"\n{GREEN}{'='*70}")
    print(f"🎉 ALL TESTS PASSED! Your API is working perfectly!")
    print(f"{'='*70}{RESET}\n")
    sys.exit(0)
else:
    print(f"\n{RED}{'='*70}")
    print(f"⚠️  Some tests failed. Review the errors above.")
    print(f"{'='*70}{RESET}\n")
    sys.exit(1)