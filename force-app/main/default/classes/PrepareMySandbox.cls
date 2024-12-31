global class PrepareMySandbox implements SandboxPostCopy {
    global PrepareMySandbox() {
        // Implementations of SandboxPostCopy must have a no-arg constructor.
        // This constructor is used during the sandbox copy process.
    }

    global void runApexClass(SandboxContext context) {
        System.debug('Org ID: ' + context.organizationId());
        System.debug('Sandbox ID: ' + context.sandboxId());
        System.debug('Sandbox Name: ' + context.sandboxName());

        updateProfilesAndResetPasswordsForPublicGroupMembers();
        // Additional logic to prepare the sandbox for use can be added here.
    }

    public void updateProfilesAndResetPasswordsForPublicGroupMembers() {
        String publicGroupId = '00G5a000003ji0R';
        String newProfileId = '00e0b000001KWuY';

        Group publicGroup = getPublicGroup(publicGroupId);

        if (publicGroup != null) {
            List<User> usersToUpdate = getUsersToUpdate(publicGroup, newProfileId);

            if (!usersToUpdate.isEmpty()) {
                update usersToUpdate;
                System.debug('Profile updated for ' + usersToUpdate.size() + ' users.');

                // Assign Author_Apex permission set
                assignAuthorApexPermissionSet(usersToUpdate);

                // Reset passwords for updated users
                resetPasswords(usersToUpdate);
            } else {
                System.debug('No eligible active users found in the Public Group.');
            }
        } else {
            System.debug('Public Group not found.');
        }
    }

    private Group getPublicGroup(String groupId) {
        return [SELECT Id FROM Group WHERE Id = :groupId LIMIT 1];
    }

    private List<User> getUsersToUpdate(Group publicGroup, String newProfileId) {
        List<User> usersToUpdate = new List<User>();
        Set<Id> userIds = new Set<Id>();

        // Get the current running User's Id
        Id currentUserId = UserInfo.getUserId();

        for (GroupMember member : [SELECT UserOrGroupId FROM GroupMember WHERE GroupId = :publicGroup.Id]) {
            Id userOrGroupId = member.UserOrGroupId;
            if (userOrGroupId != null && userOrGroupId.getSObjectType() == User.SObjectType && userOrGroupId != currentUserId) {
                userIds.add(userOrGroupId);
            }
        }

        // Query and update active User profiles
        for (User user : [SELECT Id, ProfileId, Email FROM User WHERE Id IN :userIds AND IsActive = true]) {
            user.ProfileId = newProfileId;
            // Remove .invalid from email address
            if (user.Email != null && user.Email.contains('.invalid')) {
                user.Email = user.Email.replace('.invalid', '');
            }
            usersToUpdate.add(user);
        }

        return usersToUpdate;
    }

    private void resetPasswords(List<User> users) {
        for (User u : users) {
            System.resetPassword(u.Id, true); // The second parameter generates a new password and sends an email
        }
        System.debug('Passwords reset for ' + users.size() + ' users.');
    }

    private void assignAuthorApexPermissionSet(List<User> users) {
        PermissionSet authorApexPS = [SELECT Id FROM PermissionSet WHERE Name = 'Author_Apex' LIMIT 1];
    
        // Gather user IDs
        Set<Id> userIds = new Set<Id>();
        for (User u : users) {
            userIds.add(u.Id);
        }
    
        // Query existing assignments
        List<PermissionSetAssignment> existingAssignments = [
            SELECT AssigneeId 
            FROM PermissionSetAssignment 
            WHERE AssigneeId IN :userIds 
            AND PermissionSetId = :authorApexPS.Id
        ];
        Set<Id> alreadyAssignedUserIds = new Set<Id>();
        for (PermissionSetAssignment psa : existingAssignments) {
            alreadyAssignedUserIds.add(psa.AssigneeId);
        }
    
        // Prepare new assignments for users without the permission set
        List<PermissionSetAssignment> psAssignments = new List<PermissionSetAssignment>();
        for (User u : users) {
            if (!alreadyAssignedUserIds.contains(u.Id)) {
                psAssignments.add(new PermissionSetAssignment(
                    AssigneeId = u.Id,
                    PermissionSetId = authorApexPS.Id
                ));
            }
        }
    
        // Insert new assignments
        if (!psAssignments.isEmpty()) {
            try {
                insert psAssignments;
                System.debug('Author_Apex permission set assigned to ' + psAssignments.size() + ' users.');
            } catch (DmlException ex) {
                System.debug('Error during permission set assignment: ' + ex.getMessage());
            }
        } else {
            System.debug('No new assignments required. All users already have the Author_Apex permission set.');
        }
    }    
}
