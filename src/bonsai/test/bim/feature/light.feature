@light
Feature: Light

Scenario: Viewing default solar settings
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    Then I see "Etc/GMT"

Scenario: Changing the month
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I set the "Year" property to "2024"
    And I set the "January" property to "3"
    Then I see "March"
    And I see "Sunrise: 06:08:54"

Scenario: Changing the date
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I set the "Year" property to "2024"
    And I set the "Date" property to "3"
    Then I see "Sunrise: 06:00:31"

Scenario: Changing the time
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I set the "Hour" property to "13"
    And I set the "Minute" property to "30"
    Then I see "Local Time: 13:30:00"

Scenario: Automatic timezone detection based on lat / long
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    And I set the "Year" property to "2024"
    When I set the "Latitude" property to "10.0"
    And I set the "Longitude" property to "20.0"
    Then I see "Africa/Ndjamena"
    And I see "Sunrise: 05:56:42"

Scenario: Display the sun path
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I click "Display Sun Path"
    And I set the "Sun Path Size" property to "100.0"
    Then nothing happens

Scenario: See no shadows
    Given an empty IFC project
    When I look at the "Solar Access / Shadow" panel
    Then I don't see "Sun Intensity"
    And I don't see "Shadow Intensity"

Scenario: Display shaded shadows
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I set the "Shadow Mode" property to "Shaded"
    And I set the "Shadow Intensity" property to "1.0"
    And I don't see "Sun Intensity"
    Then nothing happens

Scenario: Display rendered shadows
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I set the "Shadow Mode" property to "Rendered"
    And I set the "Sun Intensity" property to "1.0"
    And I don't see "Shadow Intensity"
    Then nothing happens

Scenario: View from sun
    Given an empty IFC project
    And I look at the "Solar Access / Shadow" panel
    When I click "View From Sun"
    Then nothing happens
