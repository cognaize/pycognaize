class login:

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def login(self):
        # Try logging in and return error if cannot
        ...

    def _create_aws_config_file(self):
        # Creates AWS config file in /tmp directory
        ...

    def _remove_aws_config(self):
        # Removes AWS config file from /tmp directory
        ...

    def __del__(self):
        # Removes AWS config file from /tmp directory
       self._remove_aws_config()