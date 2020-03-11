*** Settings ***
Library    Process
Library    OperatingSystem
Test Setup    Set Python Path
Test Teardown    Delete Project

*** Variables ***
${PROJECT_NAME}     AwesomeProject
${CPM}    ${EXECDIR}/scripts/cpm

*** Test Cases ***
Create-Project
    ${result}=    Run Process    ${CPM}    create    ${PROJECT_NAME}
    Should Be Equal 	${result.rc} 	${0}

Build-With-Sample-Code
    Run Process    ${CPM}    create    -s    ${PROJECT_NAME}
    Run Process    ${CPM}    build    cwd=${PROJECT_NAME}    alias=build
    ${result}=    Get Process Result    build
    Should Be Equal 	${result.rc} 	${0}

Build-After-Build
    Run Process    ${CPM}    create    ${PROJECT_NAME}
    Run Process    ${CPM}    build    cwd=${PROJECT_NAME}
    Run Process    ${CPM}    build    cwd=${PROJECT_NAME}    alias=build
    ${result}=    Get Process Result    build
    Should Be Equal 	${result.rc} 	${0}

Build-Fails-When-Directory-Does-Not-Contain-A-CPM-Project
    Run Process    ${CPM}    build    alias=build
    ${result}=    Get Process Result    build
    Should Be Equal 	${result.rc} 	${1}

Clean-After-Build-With-Sample-Code
    Run Process    ${CPM}    create    ${PROJECT_NAME}
    Run Process    ${CPM}    build    cwd=${PROJECT_NAME}
    Run Process    ${CPM}    clean    cwd=${PROJECT_NAME}    alias=clean
    ${result}=    Get Process Result    clean
    Should Be Equal 	${result.rc} 	${0}

Clean-Repeatedly-After-Build-With-Sample-Code
    Run Process    ${CPM}    create    ${PROJECT_NAME}
    Run Process    ${CPM}    build    cwd=${PROJECT_NAME}
    Run Process    ${CPM}    clean    cwd=${PROJECT_NAME}
    Run Process    ${CPM}    clean    cwd=${PROJECT_NAME}    alias=clean
    ${result}=    Get Process Result    clean
    Should Be Equal 	${result.rc} 	${0}

Clean-Fails-When-Directory-Does-Not-Contain-A-CPM-Project
    Run Process    ${CPM}    clean    alias=clean
    ${result}=    Get Process Result    build
    Should Be Equal 	${result.rc} 	${1}

Test-Fails-When-Directory-Does-Not-Contain-A-CPM-Project
    Run Process    ${CPM}    test    alias=test
    ${result}=    Get Process Result    test
    Should Be Equal 	${result.rc} 	${1}

Test-Command-Returns-0-When-Project-Has-No-Tests
    Run Process    ${CPM}    create    ${PROJECT_NAME}
    Run Process    ${CPM}    test      cwd=${PROJECT_NAME}    alias=test
    ${result}=    Get Process Result    test
    Should Be Equal 	${result.rc} 	${0}

*** Keywords ***
Delete Project
    Remove Directory 	${PROJECT_NAME} 	recursive=True

Set Python Path
    Set Environment Variable    PYTHONPATH    ${EXECDIR}