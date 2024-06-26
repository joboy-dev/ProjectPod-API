from django.urls import path
from . import views

app_name = 'project'

urlpatterns = [
    path('create/workspace/<uuid:workspace_id>/', views.CreateProjectView.as_view(), name='create-project'),
    path('workspace/<uuid:workspace_id>/all/', views.GetProjectsInWorkspaceView.as_view(), name='workspace-projects'),
    path('<uuid:project_id>/', views.ProjectDetailsView.as_view(), name='project-details'),
    path('<uuid:project_id>/toggle-completion-status/', views.ToggleCompletionStatusView.as_view(), name='toggle-completion-status'),
    path('<uuid:project_id>/member/<uuid:member_id>/add/', views.AddMemberToProjectView.as_view(), name='add-member-to-project'),
    path('<uuid:project_id>/member/<uuid:member_id>/remove/', views.RemoveMemberFromProjectView.as_view(), name='remove-member-from-project'),
]