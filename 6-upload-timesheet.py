"""
    Example of how to upload time for an employee.
    Typically this type of upload be run on Monday or early Tuesday for the week just ended.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.
    It also requires that there be at least one job in active state.

    To put a job into active state, you must:
     1. Invite a worker, to create the job 
     2. Login as that invited worker and complete onboarding steps
     3. Login as admin and approve the worker (Evaluations page)

    As client: you can run this example, if your client already has an active job.
    As admin: you can run this example.
"""

# setting up the example
import common
common.print_header(__file__)

# real stuff starts here
from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()
your_scope = greenlight.scope() 

###### Add hours for a worker ######

# Act I: Decide what client, job, and project the hours will be added to
job = common.choose_existing_job(greenlight)
project = common.choose_existing_project(greenlight, job['id'])
job_ext = greenlight.get_job_extended(job['id'])
print(f"  I. Hours will be added for " + common.job_to_string(job_ext) + " project=" + common.project_to_string(project))

# Act II: Create a timesheet with some shifts on it, and leave it in "to-approve state"
shifts_expenses = common.random_shifts_expenses(job['id'], project['id'])
your_timesheet_id = common.random_your_id()
timesheet_id = greenlight.create_timesheet_with_shifts_expenses(shifts_expenses, your_timesheet_id, approve=False)
print(" II. Created timesheet " + timesheet_id + " with shifts/expenses and submitted it - look for it in To Approve")

# Act II: Create a timesheet with some shifts on it, and leave it in "to-approve state"
shifts_expenses = common.random_shifts_expenses(job['id'], project['id'])
your_timesheet_id = common.random_your_id()
timesheet_id = greenlight.create_timesheet_with_shifts_expenses(shifts_expenses, your_timesheet_id, approve=True)
print("III. Created timesheet " + timesheet_id + " with shifts/expenses and approved it - look for it in Approved")

