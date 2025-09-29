import Post

for post in range(100 + 1):
   p = Post(
   title = f'{post}chungo',
   content ='contenido de calidad')
   p.save() 
