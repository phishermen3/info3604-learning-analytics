# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .log import log_views
from .course import course_views
from .courseEnrollment import courseEnrollment_views
from .team import team_views
from .teamMembership import teamMembership_views
from .admin import setup_admin
from .about import about_views
from .activityInstance import instance_views

# blueprints must be added to this list
views = [
    user_views, 
    index_views, 
    auth_views, 
    log_views, 
    course_views, 
    courseEnrollment_views, 
    team_views, 
    teamMembership_views, 
    about_views, 
    instance_views
] 
