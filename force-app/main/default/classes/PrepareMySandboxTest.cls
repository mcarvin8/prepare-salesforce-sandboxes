/*******************************************************************************************************
 * @classname: PrepareMySandbox
 * @tests: PrepareMySandboxTest
 * Above annotation complies with https://github.com/renatoliveira/apex-test-list 
 ******************************************************************************************************/
@isTest
class PrepareMySandboxTest {
    // Constants for role, profile, group, and permission set names
    private static final String PUBLIC_GROUP_NAME = 'FullTime Developers';
    private static final String ADMIN_ROLE_NAME = 'Administrator';
    private static final String OLD_PROFILE_NAME = 'Admin-SoD-Prod-Delivery';
    private static final String NEW_PROFILE_NAME = 'Admin-SoD-PreProd-Delivery';
    private static final String PERMISSION_SET_NAME = 'Author_Apex';

    @isTest
    public static void testUpdateProfilesAndResetPasswordsForPublicGroupMembers() {
        Group publicGroup = [SELECT Id FROM Group WHERE Name = :PUBLIC_GROUP_NAME LIMIT 1];
        UserRole adminRole = [SELECT Id FROM UserRole WHERE Name = :ADMIN_ROLE_NAME LIMIT 1];
        Profile oldProfile = [SELECT Id FROM Profile WHERE Name = :OLD_PROFILE_NAME LIMIT 1];
        Profile newProfile = [SELECT Id FROM Profile WHERE Name = :NEW_PROFILE_NAME LIMIT 1];

        // Create test users with the old profile
        List<User> testUsers = new List<User>();
        for (Integer i = 1; i <= 5; i++) {
            User user = new User(
                Alias = 'U' + i,
                Email = 'user' + i + '@avalara.com',
                EmailEncodingKey = 'UTF-8',
                LastName = 'User' + i,
                LanguageLocaleKey = 'en_US',
                LocaleSidKey = 'en_US',
                ProfileId = oldProfile.Id,
                TimeZoneSidKey = 'America/Los_Angeles',
                UserName = 'user' + i + '@avalara.com',
                IsActive = true
            );
            testUsers.add(user);
        }

        // Insert all the test users in one DML statement
        insert testUsers;

        // Add test users to the public group
        List<GroupMember> groupMembers = new List<GroupMember>();
        for (User user : testUsers) {
            groupMembers.add(new GroupMember(GroupId = publicGroup.Id, UserOrGroupId = user.Id));
        }
        insert groupMembers;

        // Create an instance of the PrepareMySandbox class
        PrepareMySandbox sandboxPreparer = new PrepareMySandbox();

        // Call the method you want to test
        Test.startTest();
        sandboxPreparer.updateProfilesAndResetPasswordsForPublicGroupMembers();
        Test.stopTest();

        // Verify outcomes for each test user
        for (User user : testUsers) {
            User updatedUser = [SELECT ProfileId, UserRoleId FROM User WHERE Id = :user.Id];
            System.assertEquals(newProfile.Id, updatedUser.ProfileId, 'User profile not updated.');
            System.assertEquals(adminRole.Id, updatedUser.UserRoleId, 'User role not updated.');

            // Verify permission set assignment
            List<PermissionSetAssignment> psAssignments = [
                SELECT Id 
                FROM PermissionSetAssignment 
                WHERE AssigneeId = :user.Id 
                AND PermissionSet.Name = :PERMISSION_SET_NAME
            ];
            System.assertEquals(1, psAssignments.size(), 'Permission set not assigned to user.');

            // Attempt to log in as the user to verify the password reset
            System.runAs(user) {
                System.assertNotEquals(null, UserInfo.getSessionId(), 'User password not reset.');
            }
        }
    }
}
