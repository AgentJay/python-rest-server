python-rest-server
==================

Apache Server extension to publish and document Postgresql resources as REST Web Services in an HTML Services Directory
The DOPA REST Services Directory makes available in HTML format, functions from a Postgresql database. It supports the following features to expose your data as a REST service:

* Automatically creates HTML pages from schemas and functions in a Postgresql database
* Publishes the descriptions as HTML for functions and function parameters based on COMMENTS in the database
* Creates a service page for each function in a postgresql schema including information on the parameters, descriptions, types and default values
* Creates sample REST service calls for each service

To take advantage of these features you simply need to create a function in Postgresql with a description. Optionally you can add additional information to the function such as parameter descriptions.
