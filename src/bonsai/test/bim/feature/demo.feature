# ############################################################################ #

# Hey there! Welcome to the Bonsai code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# Note: these tests are commented out as they are for learning purposes only. If
# you want to run these tests, uncomment it :)

#|# This allows us to write full integration tests that test how all systems work
#|# as a whole. Whilst other tests focus on portions of the software, these tests
#|# simulate what happens when a user opens Blender, presses buttons, and does
#|# things.
#|
#|# These tests read like english. You can see all the possible sentences defined
#|# in test_feature.py. Most of the time, there is already a sentence defined for
#|# what you want to test.
#|
#|@demo
#|Feature: Demo
#|
#|# Every operator has at least one scenario associated with it to test it.
#|Scenario: Demonstrate hello world
#|    Given an empty IFC project
#|    When I press "bim.demonstrate_hello_world"
#|    # Blender doesn't have a way of testing that things are visible in the
#|    # interface and layout. We can check properties, and what's in the 3D
#|    # scenegraph, but not layout. There is no "DOM" like in web applications.
#|    # Too bad, we can't check the results, but we still write the test, that way
#|    # we can still check for errors like crashes or Python errors, like a "smoke
#|    # test".
#|    Then nothing happens
#|
#|# This operator has two scenarios because there are two possibilities of a user
#|# interacting with it.
#|Scenario: Demonstrate rename project - with a name provided
#|    Given an empty IFC project
#|    When I set "scene.BIMDemoProperties.name" to "Foobar"
#|    And I press "bim.demonstrate_rename_project"
#|    Then the object "IfcProject/Foobar" is an "IfcProject"
#|
#|# This is the other possible scenario for the rename project operator.
#|Scenario: Demonstrate rename project - with no name
#|    Given an empty IFC project
#|    When I set "scene.BIMDemoProperties.name" to ""
#|    And I press "bim.demonstrate_rename_project"
#|    Then the object "IfcProject/My Project" is an "IfcProject"
