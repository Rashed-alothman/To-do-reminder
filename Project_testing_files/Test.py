import requests
import sys

BASE_URL = 'http://localhost:5000/homepage/api/tasks'

# Color codes for terminal output
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
print("TMS (Task Management System) - Complete API Test Suite")
print("Testing CRUD + Filtering + Sorting + Priority")
print(f"{'='*70}{RESET}\n")

# ============================================================================
# PART 1: BASIC CRUD TESTS
# ============================================================================

print_test_header(1, "Creating Tasks with Different Priorities")
priorities = ['low', 'medium', 'high', 'urgent']
try:
    for priority in priorities:
        response = requests.post(
            f'{BASE_URL}/add_Tasks',
            json={'description': f'Task with {priority} priority', 'priority': priority}
        )
        if response.status_code == 201:
            result = response.json()
            task_id = result['task']['id']
            task_ids.append(task_id)
            print_success(f"Created {priority} priority task (ID: {task_id})")
            passed += 1
        else:
            print_error(f"Failed to create {priority} task: {response.status_code}")
            failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

print_test_header(2, "Creating Tasks Without Priority (Should Default to 'low')")
try:
    response = requests.post(
        f'{BASE_URL}/add_Tasks',
        json={'description': 'Task without priority specified'}
    )
    if response.status_code == 201:
        result = response.json()
        task_id = result['task']['id']
        task_ids.append(task_id)
        print_success(f"Created task with default priority")
        print_info(f"Priority: {result['task']['priority']}")
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

print_test_header(3, "Retrieving All Tasks")
try:
    response = requests.get(f'{BASE_URL}')
    if response.status_code == 200:
        all_tasks = response.json().get('Tasks', [])
        print_success(f"Retrieved {len(all_tasks)} tasks")
        for task in all_tasks:
            status = "✓ Done" if task.get('completed') else "○ Pending"
            priority = task.get('priority', 'N/A')
            print_info(f"{status} [{priority}] {task['description'][:40]}")
        passed += 1
    else:
        print_error(f"Failed to retrieve tasks: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# PART 2: FILTERING TESTS
# ============================================================================

print_test_header(4, "Filtering: Get Only Pending Tasks")
try:
    response = requests.get(f'{BASE_URL}?completed=false')
    if response.status_code == 200:
        tasks = response.json().get('Tasks', [])
        all_pending = all(not task['completed'] for task in tasks)
        if all_pending:
            print_success(f"Retrieved {len(tasks)} pending tasks (all correct)")
        else:
            print_error("Some completed tasks were included")
            failed += 1
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

print_test_header(5, "Filtering: Get High Priority Tasks")
try:
    response = requests.get(f'{BASE_URL}?priority=high')
    if response.status_code == 200:
        tasks = response.json().get('Tasks', [])
        all_high = all(task['priority'] == 'high' for task in tasks)
        if all_high:
            print_success(f"Retrieved {len(tasks)} high priority tasks (all correct)")
        else:
            print_error("Some non-high priority tasks were included")
            failed += 1
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

print_test_header(6, "Filtering: Combine Filters (Pending + Urgent)")
try:
    response = requests.get(f'{BASE_URL}?completed=false&priority=urgent')
    if response.status_code == 200:
        tasks = response.json().get('Tasks', [])
        correct = all(not task['completed'] and task['priority'] == 'urgent' for task in tasks)
        if correct:
            print_success(f"Retrieved {len(tasks)} pending urgent tasks (correct)")
        else:
            print_error("Filter combination didn't work correctly")
            failed += 1
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# PART 3: SORTING TESTS
# ============================================================================

print_test_header(7, "Sorting: By Creation Date (Newest First)")
try:
    response = requests.get(f'{BASE_URL}?sort=created_at')
    if response.status_code == 200:
        tasks = response.json().get('Tasks', [])
        print_success(f"Retrieved {len(tasks)} tasks sorted by creation date")
        print_info("First 3 tasks (newest first):")
        for task in tasks[:3]:
            print_info(f"  - {task['description'][:40]} (created: {task['created_at']})")
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

print_test_header(8, "Sorting: By Priority (Urgent > High > Medium > Low)")
try:
    response = requests.get(f'{BASE_URL}?sort=priority')
    if response.status_code == 200:
        tasks = response.json().get('Tasks', [])
        print_success(f"Retrieved {len(tasks)} tasks sorted by priority")
        print_info("Priority order:")
        for task in tasks:
            print_info(f"  - [{task['priority']}] {task['description'][:40]}")
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

# ============================================================================
# PART 4: UPDATE AND DELETE TESTS
# ============================================================================

print_test_header(9, "Update: Change Task Description")
if task_ids:
    try:
        update_id = task_ids[0]
        response = requests.patch(
            f'{BASE_URL}/updated_task',
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
            print_error(f"Update failed: {response.status_code}")
            failed += 1
    except Exception as e:
        print_error(f"Exception occurred: {e}")
        failed += 1
else:
    print_error("No tasks available to update")
    failed += 1

print_test_header(10, "Update: Mark Task as Completed")
if len(task_ids) > 1:
    try:
        complete_id = task_ids[1]
        response = requests.patch(
            f'{BASE_URL}/updated_task',
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

print_test_header(11, "Delete: Remove a Task")
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
# PART 5: ERROR HANDLING TESTS
# ============================================================================

print_test_header(12, "Error: Add Task with Invalid Priority")
try:
    response = requests.post(
        f'{BASE_URL}/add_Tasks',
        json={'description': 'Task with bad priority', 'priority': 'super-mega-ultra'}
    )
    if response.status_code == 400:
        print_success("Correctly rejected invalid priority")
        print_info(f"Response: {response.json()}")
        passed += 1
    else:
        print_error(f"Wrong status code: {response.status_code} (expected 400)")
        failed += 1
except Exception as e:
    print_error(f"Exception occurred: {e}")
    failed += 1

print_test_header(13, "Error: Update Non-Existent Task")
try:
    response = requests.patch(
        f'{BASE_URL}/updated_task',
        json={
            'id': 'fake-uuid-9999',
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

print_test_header(14, "Error: Delete Without ID")
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

print_test_header(15, "Error: Add Task Without Description")
try:
    response = requests.post(
        f'{BASE_URL}/add_Tasks',
        json={'priority': 'high'}  # Missing description
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
# PART 6: ADVANCED FILTER COMBINATIONS
# ============================================================================

print_test_header(16, "Advanced: Filter Completed + Sort by Priority")
try:
    response = requests.get(f'{BASE_URL}?completed=true&sort=priority')
    if response.status_code == 200:
        tasks = response.json().get('Tasks', [])
        print_success(f"Retrieved {len(tasks)} completed tasks sorted by priority")
        for task in tasks[:5]:
            print_info(f"  [{task['priority']}] {task['description'][:40]}")
        passed += 1
    else:
        print_error(f"Failed: {response.status_code}")
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
            
            # Group by priority
            by_priority = {}
            for task in remaining:
                priority = task.get('priority', 'unknown')
                by_priority[priority] = by_priority.get(priority, 0) + 1
            
            print_info("Breakdown by priority:")
            for priority in ['urgent', 'high', 'medium', 'low']:
                count = by_priority.get(priority, 0)
                if count > 0:
                    print_info(f"  - {priority.capitalize()}: {count} tasks")
            
            # Show completion stats
            completed_count = sum(1 for task in remaining if task['completed'])
            print_info(f"\nCompletion status:")
            print_info(f"  - Completed: {completed_count}")
            print_info(f"  - Pending: {len(remaining) - completed_count}")
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
print("TEST SUMMARY")
print(f"{'='*70}{RESET}")
print(f"{GREEN}Passed: {passed}{RESET}")
print(f"{RED}Failed: {failed}{RESET}")
print(f"Total:  {passed + failed}")

if failed == 0:
    print(f"\n{GREEN}{'='*70}")
    print("ALL TESTS PASSED!")
    print("Your TMS API is working perfectly with all new features!")
    print("- CRUD operations")
    print("- Priority system")
    print("- Filtering by completion and priority")
    print("- Sorting by date and priority")
    print("- Comprehensive error handling")
    print(f"{'='*70}{RESET}\n")
    sys.exit(0)
else:
    print(f"\n{RED}{'='*70}")
    print("Some tests failed. Review the errors above.")
    print(f"{'='*70}{RESET}\n")
    sys.exit(1)