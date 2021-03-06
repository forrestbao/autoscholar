# Mendeley Desktop Api Retrieval

To retrieve the document using an api, follow the instruction below

- Navigate to [Mendeley Desktop Dev](https://dev.mendeley.com/)
- Register a new app, with the following information
    - Application name: Mendeley Desktop Api
    - Description: Retrieve Document Using Mendeley Desktop 
    - Redirect URL: http://localhost:5000/oauth 
- Accept the Terms and Condition
- Click On Generate Secret
- Click on Submit 

Once an app in registered, under My Application, click on the id that matches the name above.

-   ID is the ClientId 
-   Expand the ID, Click on Generate secret, and copy the new generated secret.
-   Paste the ID, and the secret under `config.yaml`
    - clientId: ID 
    - clientSecret: Secret 
    - redirectURI: Redirect URL

`config.yaml`:

    - clientId: ID
    - clientSecret: "Secret"
    - redirectURI: "http://localhost:5000/oauth"
    - username: "Your Mendeley Desktop Username"
    - password: "Your Mendeley Desktop Password"

Using our script:  

- Install Mendeley Python SDK via command `pip3 install mendeley`
- Open `extract_annot.py`. Go to the bottom, change the value in this line `groupName = 'BioNLP'`
  to the name of a Mendeley group that you own. 
- Run `extract_annot.py`. It will dump annotations into a JSON file like `annot.json`
      

