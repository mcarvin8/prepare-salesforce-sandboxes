@isTest
class PrepareMySandboxTest {
    @isTest
    public static void testUpdateProfilesForPublicGroupMembers() {
        // Create and insert test data (Public Group, Users, etc.)
        Group publicGroup = new Group(Name = 'TestPublicGroup', Type = 'Regular');
        insert publicGroup;

        Profile newProfile = [SELECT Id FROM Profile WHERE Name = 'Admin-SoD-PreProd-Delivery' LIMIT 1];
        
        List<User> testUsers = new List<User>();
        for (Integer i = 1; i <= 5; i++) {
            User user = new User(
                Alias = 'U' + i,
                Email = 'user' + i + '@domain.com',
                EmailEncodingKey = 'UTF-8',
                LastName = 'User' + i,
                LanguageLocaleKey = 'en_US',
                LocaleSidKey = 'en_US',
                ProfileId = newProfile.Id,
                TimeZoneSidKey = 'America/Los_Angeles',
                UserName = 'user' + i + '@domain.com'
            );
            testUsers.add(user);
        }

        // Insert all the test users in one DML statement
        insert testUsers;

        List<GroupMember> groupMembers = new List<GroupMember>();
        for (User user : testUsers) {
            groupMembers.add(new GroupMember(GroupId = publicGroup.Id, UserOrGroupId = user.Id));
        }
        insert groupMembers;

        // Create an instance of the PrepareMySandbox class
        PrepareMySandbox sandboxPreparer = new PrepareMySandbox();

        // Call the method you want to test
        Test.startTest();
        sandboxPreparer.updateProfilesForPublicGroupMembers();
        Test.stopTest();

        // Verify that the users' profiles have been updated as expected
        for (User user : testUsers) {
            User updatedUser = [SELECT ProfileId FROM User WHERE Id = :user.Id];
            System.assertEquals(newProfile.Id, updatedUser.ProfileId, 'User profile not updated.');
        }
    }
}
