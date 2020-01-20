*** Settings ***
Library    Process
Library    OperatingSystem
Test Teardown    Delete Project

*** Variables ***
${PROJECT_NAME}     AwesomeProject

*** Test Cases ***
Test-Project-Creation
    ${result}=    Run Process    python3.7    ./cpm.py    create    ${PROJECT_NAME}
    Should Be Equal 	${result.rc} 	${0}

Test-Target-Addition-Failure-When-No-Project
    ${result}=    Run Process    python3.7    ./cpm.py    target    add    ${PROJECT_NAME}
    Should Be Equal 	${result.rc} 	${1}

Test-Target-Addition
    Run Process    python3.7    ./cpm.py    create    ${PROJECT_NAME}
    Run Process    python3.7    ../cpm.py    target    add    ubuntu    cwd=${PROJECT_NAME}    alias=add_target
    ${result}=    Get Process Result    add_target
    Should Be Equal 	${result.rc} 	${0}

Test-Project-Build-With-Sample-Code
    Run Process    python3.7    ./cpm.py    create    -s    ${PROJECT_NAME}
    Run Process    python3.7    ../cpm.py    build    cwd=${PROJECT_NAME}    alias=build
    ${result}=    Get Process Result    build
    Should Be Equal 	${result.rc} 	${0}

*** Keywords ***
Delete Project
    Remove Directory 	${PROJECT_NAME} 	recursive=True

