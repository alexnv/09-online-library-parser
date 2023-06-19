from livereload import Server, shell


server = Server()
server.watch('./*.jinja', shell('render_website.py', cwd='.'))
server.serve(root='.')