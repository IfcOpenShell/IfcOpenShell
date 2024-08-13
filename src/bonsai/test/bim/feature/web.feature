@web
Feature: Web
    Web interface to complement Blender UI

Scenario: Start server
    Given an empty Blender session
    When I press "bim.connect_websocket_server"
    Then nothing happens

Scenario: Kill server
    Given an empty Blender session
    And I press "bim.connect_websocket_server"
    When I press "bim.kill_websocket_server"
    Then nothing happens

Scenario: Open web browser
    Given an empty Blender session
    And I press "bim.connect_websocket_server"
    When I press "bim.open_web_browser"
    Then nothing happens
