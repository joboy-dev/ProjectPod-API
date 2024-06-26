from django.contrib.auth import get_user_model
from rest_framework import serializers

from notification.models import Notification
from user.serializers import UserDetailsSerializer
from workspace.models import Member, Workspace

User = get_user_model()

class CreateWorkspaceSerializer(serializers.ModelSerializer):
    '''Serializer to create a new workspace'''
    
    creator = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'company_email', 'no_of_members_allowed', 'plan', 'creator']
        read_only_fields = ['id', 'creator']
        
    def validate(self, data):
        user = self.context['request'].user
        
        if Workspace.objects.filter(company_email=data['company_email']).exists():
            raise serializers.ValidationError({'error': 'This email is in use by another workspace'})
        
        if data['plan'] not in ['basic', 'premium', 'enterprise']:
            raise serializers.ValidationError({'error': 'This workspace plan is not available. Choose between basic, premium, and enterprise'})
        
        # -----------------------------------------------------
        # CHECK USER SUBSCRIPTION RESTRICTIONS
        # -----------------------------------------------------
        
        # For starter plan for the user's subscription
        if user.subscription_plan == 'starter':
            if Member.objects.filter(user=user).exists():
                raise serializers.ValidationError({'error': 'You are entitled to one workspace at a time. Upgrade your subscription to have access to more.'})
        
        # For pro plan for the user's subscription
        if user.subscription_plan == 'pro':
            if Member.objects.filter(user=user).count() == 3:
                raise serializers.ValidationError({'error': 'You are entitled to only three workspaces. Upgrade your subscription to have access to more.'})
        
        # For ultimate plan for the user's subscription
        if user.subscription_plan == 'ultimate':
            if Member.objects.filter(user=user).count() == 7:
                raise serializers.ValidationError({'error': 'You are entitled to seven workspaces.'})
        
        return data
        
    def create(self, validated_data):
        name = validated_data.get('name')
        company_email = validated_data.get('company_email')
        no_of_members_allowed = validated_data.get('no_of_members_allowed')
        creator = self.context['request'].user
        
        # create workspace
        workspace = Workspace.objects.create(
            name=name,
            company_email=company_email,
            no_of_members_allowed=no_of_members_allowed,
            creator=creator,
        )
        
        # Add creator to member list
        Member.objects.create(
            user=creator,
            workspace=workspace,
            role='editor',
        )
        
        # Increase number of members by 1
        workspace.current_no_of_members += 1
        workspace.save()
        
        return workspace
    

class WorkspaceDetailsSerializer(serializers.ModelSerializer):
    '''Serializer for handling workspace details'''
    
    creator = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'current_no_of_members']
        
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
            
        instance.save()
        return instance
    
class UpdateWorkspaceSubscriptionSerializer(serializers.ModelSerializer):
    '''Serializer to update subscription plan for a workspace'''
    
    class Meta:
        model = Workspace
        fields = ['id', 'plan']
        read_only_fields = ['id']
        
    def validate(self, data):
        if data['plan'] not in ['basic', 'premium', 'enterprise']:
            raise serializers.ValidationError({'error': 'This workspace plan is not available. Choose between basic, premium, and enterprise'})
        
        return data
    
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
            
        instance.save()
        return instance
    
    

class MemberSerializer(serializers.ModelSerializer):
    '''Serializer to add a member to a workspace and also get all members in a workspace'''
    
    workspace = serializers.SerializerMethodField(read_only=True)
    user = UserDetailsSerializer(read_only=True)  

    def get_workspace(self, obj):
        return obj.workspace.name
    
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['id', 'user', 'workspace', 'date_joined']
        
    def validate(self, data):
        workspace_id = self.context['view'].kwargs['workspace_id']
        user_id = self.context['view'].kwargs['user_id']
        
        workspace = Workspace.objects.get(id=workspace_id)
        user = User.objects.get(id=user_id)
        
        # -----------------------------------------------------
        # CHECK USER SUBSCRIPTION RESTRICTIONS
        # -----------------------------------------------------
        
        # For starter plan for the user's subscription
        if user.subscription_plan == 'starter':
            if Member.objects.filter(user=user).exists():
                raise serializers.ValidationError({'error': 'This user you want to add is entitled to one workspace at a time.'})
        
        # For pro plan for the user's subscription
        if user.subscription_plan == 'pro':
            if Member.objects.filter(user=user).count() == 3:
                raise serializers.ValidationError({'error': 'This user you want to add is entitled to only three workspaces.'})
        
        # For ultimate plan for the user's subscription
        if user.subscription_plan == 'ultimate':
            if Member.objects.filter(user=user).count() == 7:
                raise serializers.ValidationError({'error': 'This user you want to add is entitled to seven workspaces.'})
        
        # check if workspace is full
        if workspace.current_no_of_members == workspace.no_of_members_allowed:
            raise serializers.ValidationError({'error': 'The workspaace is full'})
        
        return data
            
    def create(self, validated_data):
        workspace_id = self.context['view'].kwargs['workspace_id']
        user_id = self.context['view'].kwargs['user_id']
        
        workspace = Workspace.objects.get(id=workspace_id)
        user = User.objects.get(id=user_id)
        role = validated_data.get('role')
        
        member = Member.objects.create(
            workspace=workspace,
            user=user,
            role=role,
        )
        
        workspace.current_no_of_members += 1
        workspace.save()
        
        # Send notification
        Notification.objects.create(
            message=f'You have been added to workspace {workspace.name}',
            sender=self.context['request'].user,  # current user
            receiver=user,  # user referenced in url with id
        )
        
        return member
    
    
class UpdateMemberSerializer(serializers.ModelSerializer):
    '''Serializer to update member role'''
    
    workspace = serializers.SerializerMethodField(read_only=True)
    user = UserDetailsSerializer(read_only=True)  

    def get_workspace(self, obj):
        return obj.workspace.name
    
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['user', 'workspace', 'date_joined']
        
    def validate(self, data):
        member = self.context['view'].kwargs['member_id']
        member = Member.objects.get(id=member)
        
        if member.user == self.context['request'].user:
            raise serializers.ValidationError({'error': 'You cannot edit your own role'})
        
        return data
        
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance
