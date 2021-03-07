from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from .models import Gene, Dataset, Cluster, Annotation
from .forms import UserForm
from .tasks import task_wrapper
import magnet_app.helper as helper
import pandas as pd

# Create your views here.
def index(request):
    '''
    View for index page

    Context:
        form: UserForm object from forms.py
        database_numbers {list}: number of genes and datasets in database
        dataset_list {list}: list of dataset names

    '''

     # retrieve the number of gene and dataset entries in MAGNET database
    database_numbers = [Gene.objects.count(), Dataset.objects.count()]
    # retrieve the names of datasets in MAGNET database
    dataset_list = Dataset.objects.values_list('dataset_name', flat=True)
    
    form = UserForm()
    context = {'database_numbers': database_numbers, 'dataset_list': dataset_list, 'form': form}
    
    return render(request, 'magnet_app/index.html', context)

def dataset_info(request, dataset_id):
    '''
    View for dataset info page

    Context:
        dataset: dataset object
        cluster_gene_num {dict}: number of genes associated with each cluster of the dataset
        total_gene_num {int}: total number of genes associated with dataset


    '''

    dataset = get_object_or_404(Dataset, pk=dataset_id)
    cluster_gene_num, total_gene_num = dataset.get_clusters()

    context = {'dataset':dataset,'cluster_gene_num':cluster_gene_num, 'total_gene_num':total_gene_num}
            
    return render(request, 'magnet_app/dataset_info.html', context)

def processing(request):

    ''' View for sending user inputted data for processing in celery and rendering progress bar '''

    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = UserForm(request.POST, request.FILES)
        
        # Check if the form is valid:
        if form.is_valid():
            
            # parse form
            user_data = helper.form_processing(request, form)
            #print(user_data)
            
            # call celery task
            magnet_task = task_wrapper.delay(user_data)
            request.session['magnet_task_id'] = magnet_task.id

            return render(request, 'magnet_app/progress.html', context={'task_id': magnet_task.task_id})
            #return HttpResponse("Placeholder")
        
        else:
            # retrieve the number of gene and dataset entries in MAGNET database
            database_numbers = [Gene.objects.count(), Dataset.objects.count()]
            # retrieve the names of datasets in MAGNET database
            dataset_list = Dataset.objects.values_list('dataset_name', flat=True) 
    
            print(form.errors)
    
            context = {'database_numbers': database_numbers, 'dataset_list': dataset_list, 'form': form}
    
            return render(request, 'magnet_app/index.html', context)

def results(request):

    ''' View for receiving hypergeometric results from celery worker and rendering results '''
    
    task_id = request.session.get('magnet_task_id')
    magnet_task = task_wrapper.AsyncResult(task_id)
    
    if magnet_task.state == 'SUCCESS':
        celery_result = magnet_task.get()
        #request.session['session_data'] = celery_result[1]
        
        context = celery_result[0]
        #print(context["user_dataset_dict"])

       # create some context to send over to Dash:
        dash_context = request.session.get("django_plotly_dash", {})
        dash_context['django_to_dash_context'] = context
        request.session['django_plotly_dash'] = dash_context
        
        return render(request,'magnet_app/results.html', context)
    else:
        return HttpResponse("Something went wrong!")


def documentation(request):
    '''
    View for documentation pages

    Context:
        nav {tuple}: activation buttons for tabs
        content {tuple}: show or hide content for each tab

    '''
    if request.method=='GET':
        page = request.GET.get('page')

        if page == "usage":
            nav = ("active","","")
            content = ("active","fade","fade")
        elif page == "faq":
            nav = ("","active","")
            content = ("fade","active","fade")
        else:
            nav = ("","","active")
            content = ("fade","fade","active")
            
        context = {'nav':nav,'content':content}

        return render(request,'magnet_app/documentation.html', context)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')('<h1>Page not found</h1>')

def search(request):
    '''
    View for gene search function

    Context:
        query_string {str}: user supplied gene symbol to search
        found entries: annotation objects that matches user query

    '''

    query_string = ''
    found_entries = None
    
    if request.GET.get('search'):
        query_string = request.GET.get('search')
        found_entries = helper.search_genes(query_string)
        
    else: 
        print("False")

    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", {})
    dash_context['search_context'] = { 'found_entries': found_entries}
    request.session['django_plotly_dash'] = dash_context

    return render(request,'magnet_app/search.html', {})

    
def download(request, **kwargs):
    
    ''' View function to download significant results entries as csv file '''

    context = request.session.get('django_plotly_dash', {})
    sig_dict = context.get('dash_to_django_context', 0)
    sig_df = pd.DataFrame.from_dict(sig_dict)
    sig_df = sig_df[['user_cluster','dataset_name','cluster_description','pval','adjusted_pval','parameters','overlap_genes']]
    sig_df.columns = ['User cluster', 'Dataset', 'Dataset cluster', 'P-value', 'Adjusted P-Value (FDR)', 'Parameters (N, B, n, b)', 'Overlapped Genes']
    sig_df = sig_df.to_csv(index=False) # cast to csv string

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="magnet_results.csv"'
    response.write(sig_df)

    return response



