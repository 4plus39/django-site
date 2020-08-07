from django.shortcuts import render
import os

# Create your views here.
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def home(request):
    return render(request, 'home.html')


def simple_upload(request):
    # delete all media/file
    # for file in os.listdir('media'):
    #     path = 'media/'+file
    #     os.remove(path)

    uploaded_file_url_lst = []
    
    if request.method == 'POST' and request.FILES['files']:
        print()
        print(request.FILES['files'])
        print()
        for file in request.FILES.getlist('files'):
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            uploaded_file_url_lst.append(fs.url(filename))

        off_part_lst = []

        with open('media/2019-12-20-1395A3191701-X01-5.bom', 'r') as f:
            for i in range(4):
                f.readline()

            for line in f.readlines():
                bom_lst = line.split('\t')
                for part in bom_lst[8].split(','):
                    if part != '-' and bom_lst[1] == '1395A3191701':
                        off_part_lst.append(part)

        with open('media/A3191701.txt', 'r') as f:
            lines = f.readlines()

        with open('media/A3191701.txt', 'w') as f:
            for line in lines:
                txt_lst = line.split('\t')
                if txt_lst[5] == 'X\n' and txt_lst[2] in off_part_lst:
                    txt_lst[5] = ' \n'

                content = ''
                for i in range(len(txt_lst)):
                    content = content + txt_lst[i]
                    if i != len(txt_lst) - 1:
                        content = content + '\t'
                f.write(content)

        message = 'File uploaded and modified, click txt link to download'

        return render(request, 'simple_upload.html', {
            'uploaded_file_url_lst': uploaded_file_url_lst,
            'message': message
        })
    return render(request, 'simple_upload.html')


def test(request):
    return render(request, 'home.html')
