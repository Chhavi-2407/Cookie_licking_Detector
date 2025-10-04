# import os
# from datetime import datetime, timedelta
# from github import Github

# from dotenv import load_dotenv




# # --- Configuration Constants ---
# # Default grace period (days) based on existing unassignment actions [2]
# DEFAULT_GRACE_PERIOD_DAYS = 7
# # Final grace period after the warning nudge is sent (hours)
# FINAL_GRACE_HOURS = 48 

# # Labels used to calculate the Dynamic Grace Period (DGP)
# COMPLEXITY_MAP = {
#     "difficulty: easy": 3,
#     "difficulty: medium": 7,  # Will use the default value
#     "difficulty: hard": 14,
# }

# # The explicit keyword required to retain the claim during the warning period (The Commitment Nudge)
# COMMITMENT_KEYWORD = "/commit-retain"
# # The label applied when an issue is detected as Stalled
# STALLED_LABEL = "Stalled-Claim"

# # --- Behavioral Nudge Messages ---
# WARNING_COMMENT = (
#     "**🚨 Commitment Nudge: Are You Still Working on This?**\n\n"
#     "We have detected that no code artifacts (commits/PRs) have been linked to this assigned issue for "
#     "longer than the expected grace period. This blocks community progress.\n\n"
#     "If you wish to retain this claim, please link a branch or comment with the explicit keyword "
#     "`{keyword}` within **{hours} hours**. Otherwise, the system will **automatically release** "
#     "the claim to unblock community progress.\n\n"
#     "If you are blocked, please apply the label `/request-maintainer-help` for specialized assistance."
# ).format(keyword=COMMITMENT_KEYWORD, hours=FINAL_GRACE_HOURS)

# RELEASE_COMMENT = (
#     "**✅ Claim Released!**\n\n"
#     "This issue has been automatically unassigned due to non-commitment (no linked code and no "
#     "retention action taken within the final grace period). This issue is now immediately available.\n\n"
#     "*(Social Proof Nudge: We encourage you to claim this! [X] similar beginner-friendly issues "
#     "have been resolved by new contributors this week. We look forward to your contribution!)*"
# )

# def calculate_dynamic_grace_period(issue):
#     """
#     Calculates the Dynamic Grace Period (DGP) in days based on issue labels.
#     A hard issue gets a longer period, an easy issue gets a shorter one.
#     """
#     dgp = DEFAULT_GRACE_PERIOD_DAYS
#     for label in issue.labels:
#         label_name = label.name.lower()
#         if label_name in COMPLEXITY_MAP:
#             dgp = COMPLEXITY_MAP[label_name]
#             # Immediately return the most specific complexity label found
#             return dgp
#     return dgp

# def check_for_code_linkage(issue):
#     """
#     SIMULATION for Code Linkage Count (CLC) check (Hackathon MVP).
    
#     In a full implementation, this would query Augur/Git logs.[3, 4]
#     For the hackathon, we simulate CLC > 0 if:
#     1. A Pull Request (PR) is linked via comments/timeline events.
#     2. An assignee has posted the specific commitment keyword to reset the final grace.
#     """
#     # Check for linked PRs or commits in the issue's timeline (CLC > 0)
#     # The PyGithub event timeline is checked for events indicating code linkage
#     events = issue.get_timeline()
#     for event in events:
#         if event.event in ["cross-referenced", "referenced", "connected"]:
#              # This indicates a PR/commit linkage in the timeline
#              return True

#     # Check the comments for the explicit commitment keyword (Micro-Commitment)
#     comments = issue.get_comments()
#     for comment in comments:
#         # Check if the assignee has posted the retention keyword 
#         if comment.user.login == issue.assignee.login and COMMITMENT_KEYWORD in comment.body:
#             return True
            
#     return False # CLC = 0 (No linked code or commitment found)


# def process_assigned_issues(repo_name, github_token):
#     """
#     Main loop to run the CLD Detection Algorithm and State Machine.
#     """
#     g = Github(github_token)
#     repo = g.get_repo(repo_name)
    
#     # Filter for all open and assigned issues
#     assigned_issues = repo.get_issues(state='open', assignee='*')
    
#     for issue in assigned_issues:
#         # Skip Pull Requests (GitHub treats PRs as issues)
#         if issue.pull_request:
#             continue
            
#         assignee_login = issue.assignee.login
#         issue_has_stalled_label = STALLED_LABEL in [label.name for label in issue.labels]
        
#         # Calculate Assignment Age (A_Age)
#         # Using the issue creation date as a proxy for assignment start in this simplified model.
#         # For full accuracy, we'd search the event timeline for the 'assigned' event date.
#         a_age_days = (datetime.now() - issue.created_at.replace(tzinfo=None)).days 

#         # Calculate Dynamic Grace Period (DGP)
#         dgp_days = calculate_dynamic_grace_period(issue)

#         # Check for Code Linkage Count (CLC)
#         clc_found = check_for_code_linkage(issue)

        
#         if clc_found:
#             # State: Progressing (CLC > 0). Remove warning label if present.
#             if issue_has_stalled_label:
#                 issue.remove_from_labels(STALLED_LABEL)
#             continue

#         # --- Detection: Stalled State Check ---
#         # Condition: A_Age > DGP AND CLC = 0
#         if a_age_days > dgp_days and not clc_found:
#             if not issue_has_stalled_label:
#                 # Action 1: Apply Nudge (Issue transitions to Stalled/Warning State)
#                 print(f"Issue #{issue.number} is Stalled. Sending 48-Hour Nudge to {assignee_login}.")
#                 issue.add_to_labels(STALLED_LABEL)
#                 issue.create_comment(WARNING_COMMENT)

#             else:
#                 # Action 2: Check Final Grace Period for Automated Release
#                 # Check if the STALLED_LABEL was applied more than FINAL_GRACE_HOURS ago
                
#                 # Find the date the STALLED_LABEL was applied
#                 stalled_label_events = repo.get_issues_events(issue.number)
#                 stalled_time = None
#                 for event in stalled_label_events:
#                     if event.event == 'labeled' and event.label.name == STALLED_LABEL:
#                         stalled_time = event.created_at.replace(tzinfo=None)
#                         break
                
#                 if stalled_time and (datetime.now() - stalled_time) > timedelta(hours=FINAL_GRACE_HOURS):
#                     # Action 2: Automated Release (Unassign/Remove Label) [1, 2]
#                     print(f"Issue #{issue.number} expired final grace. Releasing claim from {assignee_login}.")
#                     issue.remove_from_labels(STALLED_LABEL)
#                     issue.remove_assignees(assignee_login)
#                     issue.create_comment(RELEASE_COMMENT)
#                 else:
#                     print(f"Issue #{issue.number} is in final grace period. Waiting for action.")
        
#         else:
#             # State: Monitored/Claimed. Not yet stalled.
#             print(f"Issue #{issue.number} assigned to {assignee_login}. Progress OK, {a_age_days}/{dgp_days} days elapsed.")
    
#     print("CLD run complete.")

# if __name__ == "__main__":
#     try:
#         # GitHub Token is secured via environment variables in GitHub Actions [2]
#         # token = os.environ
#         # The repository is pulled from the action's context
#         # repo_slug = os.environ
#         load_dotenv()  # Load values from .env

#         token = os.environ["GITHUB_TOKEN"]
#         repo_slug = os.environ["GITHUB_REPOSITORY"]
        
#         process_assigned_issues(repo_slug, token)
        
#     except KeyError as e:
#         print(f"Error: Missing environment variable {e}. Ensure GITHUB_TOKEN and GITHUB_REPOSITORY are set.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")




import os
from datetime import datetime, timedelta
from github import Github, Auth
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
try:
    token = os.environ["GITHUB_TOKEN"]
    repo_slug = os.environ["GITHUB_REPOSITORY"]
except KeyError as e:
    print(f"Error: Missing environment variable {e}. Ensure GITHUB_TOKEN and GITHUB_REPOSITORY are set.")
    exit(1)

# --- Configuration Constants ---
DEFAULT_GRACE_PERIOD_DAYS = 7
FINAL_GRACE_HOURS = 48

COMPLEXITY_MAP = {
    "difficulty: easy": 3,
    "difficulty: medium": 7,
    "difficulty: hard": 14,
}

COMMITMENT_KEYWORD = "/commit-retain"
STALLED_LABEL = "Stalled-Claim"

WARNING_COMMENT = (
    "**🚨 Commitment Nudge: Are You Still Working on This?**\n\n"
    "We have detected that no code artifacts (commits/PRs) have been linked to this assigned issue for "
    "longer than the expected grace period. This blocks community progress.\n\n"
    "If you wish to retain this claim, please link a branch or comment with the explicit keyword "
    "`{keyword}` within **{hours} hours**. Otherwise, the system will **automatically release** "
    "the claim to unblock community progress.\n\n"
    "If you are blocked, please apply the label `/request-maintainer-help` for specialized assistance."
).format(keyword=COMMITMENT_KEYWORD, hours=FINAL_GRACE_HOURS)

RELEASE_COMMENT = (
    "**✅ Claim Released!**\n\n"
    "This issue has been automatically unassigned due to non-commitment (no linked code and no "
    "retention action taken within the final grace period). This issue is now immediately available.\n\n"
    "*(Social Proof Nudge: We encourage you to claim this! [X] similar beginner-friendly issues "
    "have been resolved by new contributors this week. We look forward to your contribution!)*"
)

# --- Helper Functions ---
def calculate_dynamic_grace_period(issue):
    dgp = DEFAULT_GRACE_PERIOD_DAYS
    for label in issue.labels:
        label_name = label.name.lower()
        if label_name in COMPLEXITY_MAP:
            return COMPLEXITY_MAP[label_name]
    return dgp

def check_for_code_linkage(issue):
    try:
        events = issue.get_timeline()
        for event in events:
            if event.event in ["cross-referenced", "referenced", "connected"]:
                return True
        comments = issue.get_comments()
        for comment in comments:
            if issue.assignee and comment.user.login == issue.assignee.login and COMMITMENT_KEYWORD in comment.body:
                return True
    except Exception:
        pass
    return False

def process_assigned_issues(repo_name, github_token):
    try:
        g = Github(auth=Auth.Token(github_token))
        repo = g.get_repo(repo_name)
    except Exception as e:
        print(f"Error connecting to repo '{repo_name}': {e}")
        return

    print(f"Connected to repository: {repo.full_name}")

    assigned_issues = repo.get_issues(state='open', assignee='*')
    for issue in assigned_issues:
        if issue.pull_request:
            continue

        assignee_login = issue.assignee.login if issue.assignee else "Unassigned"
        issue_has_stalled_label = STALLED_LABEL in [label.name for label in issue.labels]

        a_age_days = (datetime.now() - issue.created_at.replace(tzinfo=None)).days
        dgp_days = calculate_dynamic_grace_period(issue)
        clc_found = check_for_code_linkage(issue)

        if clc_found:
            if issue_has_stalled_label:
                issue.remove_from_labels(STALLED_LABEL)
            continue

        if a_age_days > dgp_days and not clc_found:
            if not issue_has_stalled_label:
                print(f"Issue #{issue.number} is Stalled. Sending 48-Hour Nudge to {assignee_login}.")
                issue.add_to_labels(STALLED_LABEL)
                issue.create_comment(WARNING_COMMENT)
            else:
                stalled_label_events = repo.get_issues_events(issue.number)
                stalled_time = None
                for event in stalled_label_events:
                    if event.event == 'labeled' and event.label.name == STALLED_LABEL:
                        stalled_time = event.created_at.replace(tzinfo=None)
                        break
                if stalled_time and (datetime.now() - stalled_time) > timedelta(hours=FINAL_GRACE_HOURS):
                    print(f"Issue #{issue.number} expired final grace. Releasing claim from {assignee_login}.")
                    issue.remove_from_labels(STALLED_LABEL)
                    if issue.assignee:
                        issue.remove_assignees(assignee_login)
                    issue.create_comment(RELEASE_COMMENT)
                else:
                    print(f"Issue #{issue.number} is in final grace period. Waiting for action.")
        else:
            print(f"Issue #{issue.number} assigned to {assignee_login}. Progress OK, {a_age_days}/{dgp_days} days elapsed.")

    print("CLD run complete.")

# --- Main Execution ---
if __name__ == "__main__":
    try:
        process_assigned_issues(repo_slug, token)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
