*** Settings ***
Library    Process

*** Test Cases ***
Test-Creation-API
    ${result}=    Run Process    python3.7    ./cpm.py    create    AwesomeProject
    Should Be Equal 	${result.rc} 	${0}

