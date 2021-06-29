Run the create zip file batch script ./0-create-zip.bat for Windows and shell script ./0-create-zip.sh for Linux
Run the deployment batch script ./1-deploy-zip.bat for Windows and shell script ./1-deploy-zip.sh for Linux
Publish a new version and take note of the version number you will need it for the next command aws lambda publish-version --function-name optOutPhoneNumbers
Assign the new version to the DEV alias aws lambda update-alias --function-name optOutPhoneNumbers --name "DEV" --function-version "<version_from_previous_step>"