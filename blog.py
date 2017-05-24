#!/usr/bin/python
# encoding: utf-8
import os
import sys
from datetime import datetime
from workflow import Workflow

log = None
wf = Workflow()

jekyll_dir = os.environ['jekyll_dir']

def parse_command(command_str):
    command = {}
    log.info(command_str)
    if len(command_str) > 0:
        key, val = command_str.split(':')
        command[key] = val
    return command

def read_stored_command(command):
    query_file = Workflow().workflowfile('query')
    try:
        with open(query_file, 'r') as f:
            for line in f:
                key, val = line.split(':')
                if key not in command:
                    command[key] = val.strip()
                elif not command[key]:
                    command[key] = val.strip()
    except IOError:
        pass
    with open(query_file, 'w') as f:
        for key, val in command.items():
            f.write("{}:{}\n".format(key, val))

    return command

def post(command):
    command = parse_command(command)
    log.info(command)
    command = read_stored_command(command)
    log.info(command)

    wf.add_item('Done!', valid=True)
    wf.add_item('Title:',
            'Write down your title' if 'title' not in command else command['title'],
            autocomplete="post title:")
    wf.add_item('Author:',
            'Write down your title' if 'author' not in command else command['author'],
            autocomplete="post author:")
    wf.add_item('Categories:',
            'Write down your categories' if 'categories' not in command else command['categories'],
            autocomplete="post categories:")
    wf.add_item('Tags:',
            'Write down your tags' if 'tags' not in command else command['tags'],
            autocomplete="post tags:")
    wf.add_item('Image:',
            'Write down your image' if 'image' not in command else command['image'],
            autocomplete="post image:")
    wf.add_item('layout:',
            'Write down your layout' if 'layout' not in command else command['layout'],
            autocomplete="post layout:")
def commit_post():

    command = read_stored_command({})
    post_dir = jekyll_dir+'/_posts'
    post_file = post_dir + '/{}.md'.format(
            datetime.now().strftime("%Y-%m-%d-")+'-'.join(command['title'].split(' ')))
    with open(post_file, 'w') as f:
        f.write('---\n')
        for key in ['layout', 'title', 'author', 'categories', 'tags', 'date', 'image']:
            if key == 'title' or key == 'author':
                f.write('{}: "{}"\n'.format(key, command.get(key, '')))
            elif key == 'tags':
                f.write('{}: [{}]\n'.format(key, command[key]))
            elif key == 'date':
                f.write('date: {:%Y-%m-%d %H:%M:%S}\n'.format(datetime.now()))
            elif key == 'image':
                f.write('image:\n')
                f.write('  feature:\n')
                f.write('  teaser:\n')
                f.write('  credit:\n')
                f.write('  creditlink:\n')
            else:
                f.write('{}: {}\n'.format(key, command.get(key, '')))
        f.write('---\n')
    os.system('open {}'.format(post_file))



def route(args):
    handler = None
    command = []
    command_string = ''
    action = ''

    if args[0] == '--commit':
        log.info("Enter action")
        commit_post()
    elif args[0] == 'preview':
        preview()
    elif args[0] == 'publish':
        publish()
    elif args:
        command_string = args[0]

    command = [c.strip() for c in command_string.split(' ')]
    log.info(command)

    if command[0] == 'post':
        handler = post
    else:
        wf.add_item('Write a new post', 'to {}/_post'.format(jekyll_dir),
                autocomplete="post")
        # wf.add_item('Preview my blog', 'from {}'.format(jekyll_dir),
        #         autocomplete="preview",
        #         valid=True,
        #         arg='--preview')
        # wf.add_item('Publish my blog', '',
        #         autocomplete="publish",
        #         valid=True,
        #         arg='--publish')

    if handler:
        handler(' '.join(command[1:]))



def main(wf):

    args = wf.args
    route(args)

    # Send output to Alfred
    wf.send_feedback()


if __name__ == '__main__':
    # Assign Workflow logger to a global variable for convenience
    log = wf.logger
    sys.exit(wf.run(main))
