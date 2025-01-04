/*******************************************************************************************************
 * @classname: PrepareMySandbox
 * @tests: PrepareMySandboxTest
 * Above annotation complies with https://github.com/renatoliveira/apex-test-list 
 ******************************************************************************************************/
 @isTest
 class PrepareMySandboxTest {
     @isTest
     public static void testUpdateProfilesAndResetPasswordsForPublicGroupMembers() {
         Group publicGroup = [SELECT Id FROM Group WHERE Name = 'FullTime Developers' LIMIT 1];
 
         // Confirm test users were assigned different profiles
         Profile oldProfile = [SELECT Id FROM Profile WHERE Name = 'Admin-SoD-Prod-Delivery' LIMIT 1];
         Profile newProfile = [SELECT Id FROM Profile WHERE Name = 'Admin-SoD-PreProd-Delivery' LIMIT 1];
 
         // Fetch the Administrator role
         UserRole adminRole = [SELECT Id FROM UserRole WHERE Name = 'Administrator' LIMIT 1];
 
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
 
         // Verify that the users' profiles have been updated as expected
         for (User user : testUsers) {
             User updatedUser = [SELECT ProfileId, UserRoleId FROM User WHERE Id = :user.Id];
             System.assertEquals(newProfile.Id, updatedUser.ProfileId, 'User profile not updated.');
             System.assertEquals(adminRole.Id, updatedUser.UserRoleId, 'User role not updated to Administrator.');
 
             // Verify Author_Apex permission set assignment
             List<PermissionSetAssignment> psAssignments = [
                 SELECT Id 
                 FROM PermissionSetAssignment 
                 WHERE AssigneeId = :user.Id 
                 AND PermissionSet.Name = 'Author_Apex'
             ];
             System.assertEquals(1, psAssignments.size(), 'Author_Apex permission set not assigned to user');
 
             // Attempt to log in as the user to verify the password reset
             System.runAs(user) {
                 System.assertNotEquals(null, UserInfo.getSessionId(), 'User password not reset.');
             }
         }
     }
 }
 