import markdown

def convert_changelog_to_html(data):
    with open('CHANGELOG.md', 'r') as f:
        text = f.read()
        html = markdown.markdown(text)


    with open('templates/CHANGELOG.html', 'w') as f:
        f.write("{% extends '_base.html' %}\n")
        f.write("{% load static %}\n")
        f.write("{% block title %}NPO-RM Changelog {% endblock title %}\n")
        f.write("{% block content %}\n")
        f.write("<div class='container-fluid pl-3'>\n")
        f.write("<br>\n")
        f.write(html)
        f.write("\n</div>\n")
        f.write("{% endblock content %}\n")
