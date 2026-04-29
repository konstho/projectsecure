## Applied Web Application Security Course Project

I created a small interactive shop web site using flask and it runs locally form my pycharm. It has three vulnerabilities.

1. SQL Injeciton: Using this command in the search bar:' UNION SELECT id, usernames, password FROM 0 users--
This will list out all the usernames and passwords

2. Stored-XSS and session hijack: In the web site you can leave a review for a product. Logged in as a user you can leave a review to one of the products and you can leave this script: <script>new Image().src='/steal?c='+document.cookie</script>
This will run silently for anyone who will access the review page. It will steal their cookie session and send it to the hackers endpoint, /stolen. Hacker can then use this session cookie to login e.g. as admin.

3. IDOR: You can view ur personal orders that will also reveal address, phone number etc. with IDOR you can then just change the url and view others orders and see their personal information.
