from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from notification.models import Notification
from workspace.models import Member, Workspace
from workspace.permissions import IsWorkspaceOwnerOrEditorOrReadOnly

from . import serializers

User = get_user_model()

class CreateWorkspaceView(generics.CreateAPIView):
    '''View to create workspace'''
    
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateWorkspaceSerializer
    
    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class WorkspaceDetailsView(generics.RetrieveUpdateDestroyAPIView):
    '''View to get, update and delete workspace details'''
    
    permission_classes = [IsAuthenticated, IsWorkspaceOwnerOrEditorOrReadOnly]
    serializer_class = serializers.WorkspaceDetailsSerializer
    
    def get(self, request, *args, **kwargs):        
        try:
            workspace = Workspace.objects.get(id=self.kwargs['workspace_id'])
            serializer = self.serializer_class(workspace)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    def get_object(self):
        workspace = Workspace.objects.get(id=self.kwargs['workspace_id'])
        self.check_object_permissions(self.request, workspace)
        return workspace
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
        try:
            super().delete(request, *args, **kwargs)
            return Response({'message': 'Workspace deleted'}, status=status.HTTP_200_OK)
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace does not exist'}, status=status.HTTP_404_NOT_FOUND)
        

class UpdateWorkspaceSubscriptionView(generics.UpdateAPIView):
    '''View to update a worjspace subscription'''
    
    serializer_class = serializers.UpdateWorkspaceSubscriptionSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceOwnerOrEditorOrReadOnly]
    
    def get_object(self):
        workspace = Workspace.objects.get(id=self.kwargs['workspace_id'])
        self.check_object_permissions(self.request, workspace)
        return workspace
    
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'message': 'Subscription plan updated successfully.'}, status=status.HTTP_200_OK)
    
    
class AddMemberToWorkspaceView(generics.CreateAPIView):
    '''View to add a member to workspace'''
    
    permission_classes = [IsAuthenticated, IsWorkspaceOwnerOrEditorOrReadOnly]
    serializer_class = serializers.MemberSerializer
    
    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        
        workspace = Workspace.objects.get(id=self.kwargs['workspace_id'])
        # Check permission class
        self.check_object_permissions(self.request, workspace)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class RemoveMemberFromWorkspaceView(generics.GenericAPIView):
    '''View to remove member from workspace'''
    
    permission_classes = [IsAuthenticated, IsWorkspaceOwnerOrEditorOrReadOnly]
    serializer_class = serializers.MemberSerializer
    
    def post(self, request, workspace_id, member_id):
        workspace = Workspace.objects.get(id=workspace_id)
        member = Member.objects.get(id=member_id, workspace=workspace)
        
        self.check_object_permissions(request, obj=workspace)
        
        if member.user == request.user:
            return Response({'error': 'You cannot remove yourself from the workspace'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                # get member to delete based on the workspace and user objects
                member.delete()
                
                workspace.current_no_of_members -= 1
                workspace.save()
                
                Notification.objects.create(
                    message=f'You have been removed from workspace {workspace.name}',
                    sender=request.user,  # current user
                    receiver=member.user,  # user referenced in url with id
                )
                
                return Response({'message': f'Member {member.user.email} has been removed'})
            
            except Member.DoesNotExist:
                return Response({'error': 'Member does not exist in workspace'}, status=status.HTTP_404_NOT_FOUND)
            

class GetWorkspaceMembersView(generics.ListAPIView):
    '''View to view all workspace members'''
    
    permission_classes = [IsAuthenticated, IsWorkspaceOwnerOrEditorOrReadOnly]
    serializer_class = serializers.MemberSerializer
    
    def get_queryset(self):
        workspace_id = self.kwargs['workspace_id']
        workspace = Workspace.objects.get(id=workspace_id)
        
        members = Member.objects.filter(workspace=workspace)
        return members
    
    def list(self, request, *args, **kwargs):
        workspace_id = self.kwargs['workspace_id']
        workspace = Workspace.objects.get(id=workspace_id)
        
        members = Member.objects.filter(workspace=workspace)
        serializer = self.serializer_class(members, many=True)
        
        if members.exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'There are no members in this workspace'}, status=status.HTTP_204_NO_CONTENT)
        
    
class UpdateMemberRoleView(generics.UpdateAPIView):
    '''View to update workspace member role'''
    
    permission_classes = [IsAuthenticated, IsWorkspaceOwnerOrEditorOrReadOnly]
    serializer_class = serializers.UpdateMemberSerializer
    
    def get_object(self):
        workspace = Workspace.objects.get(id=self.kwargs['workspace_id'])
        
        member = Member.objects.get(id=self.kwargs['member_id'], workspace=workspace)
        
        self.check_object_permissions(self.request, obj=workspace)
        return member
        
    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        try:
            workspace = Workspace.objects.get(id=self.kwargs['workspace_id'])
            member = Member.objects.get(id=self.kwargs['member_id'], workspace=workspace)
            Notification.objects.create(
                message=f'Youur role has been updated in {workspace.name}. You are now a/an {member.role}.',
                sender=self.request.user,  # current user
                receiver=member.user,  # user referenced in url with id
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            return Response({'error': 'Member does not exist in workspace'}, status=status.HTTP_404_NOT_FOUND)
            
    