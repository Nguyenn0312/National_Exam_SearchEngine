from django.shortcuts import render
from django.db.models import Q
from .models import ExamResult
from .serializers import ExamResultSerializer
from rest_framework import generics, filters

def search_results(request, search_query=None):
    query = search_query.strip().lower() if search_query else ''
    results_queryset = []

    if query:
        #Search by SBD (ID)
        if query.isdigit():
            results_queryset = ExamResult.objects.filter(sbd=query)
        
        #Search by Subject Name
        else:
            #Check if the query matches database column names
            valid_subjects = ['math', 'literature', 'physic', 'chemistry', 'biology', 'history', 'geography', 'civic', 'language_score']
            
            if query in valid_subjects:
                # Get students who actually have a score for this subject
                filter_kwargs = {f"{query}__isnull": False}
                results_queryset = ExamResult.objects.filter(**filter_kwargs)[:100]

    # Process results into the dictionary format for the HTML
    processed_results = []
    field_names = ['literature', 'math', 'physic', 'chemistry', 'biology', 'history', 'geography', 'civic', 'language_score']

    for student in results_queryset:
        student_subjects = []
        for field in field_names:
            score = getattr(student, field)
            if score is not None:
                display_name = field.replace('_score', '').capitalize()
                student_subjects.append({'name': display_name, 'score': score})
        
        processed_results.append({
            'sbd': student.sbd,
            'subjects': student_subjects
        })

    return render(request, 'search.html', {'results': processed_results, 'query': query})

class StudentDetailAPI(generics.RetrieveAPIView):
          queryset = ExamResult.objects.all()
          serializer_class = ExamResultSerializer
          lookup_field = 'sbd'
        # Unified Search & Filter Endpoint
class StudentListAPI(generics.ListAPIView):
          queryset = ExamResult.objects.all()
          serializer_class = ExamResultSerializer
          filter_backends = [filters.SearchFilter]
          search_fields = ['sbd'] 
       # Specialized Filtering Endpoint
class FilterAPI(generics.ListAPIView):
         queryset = ExamResult.objects.all()
         serializer_class = ExamResultSerializer
    
       # This enables /api/filter?math=9.0&literature=8.5
         filterset_fields = ['math', 'literature', 'physic', 'chemistry']
