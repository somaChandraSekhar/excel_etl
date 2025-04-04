import pandas as pd
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Company
from .serializers import CompanySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company model with custom actions for file upload and data generation
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
    @action(detail=False, methods=['POST'])
    def upload_excel(self, request):
        """Upload Excel file and save data to database"""
        try:
            excel_file = request.FILES.get('file')
            if not excel_file:
                return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Check file extension
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                return Response({'error': 'File must be .xlsx or .xls'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Validate required columns
            required_columns = ['name', 'revenue', 'profit', 'employees', 'country']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response({
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Import data
            companies = []
            for _, row in df.iterrows():
                company = Company.objects.create(
                    name=row['name'],
                    revenue=row['revenue'],
                    profit=row['profit'],
                    employees=row['employees'],
                    country=row['country']
                )
                companies.append(company)
            
            serializer = self.get_serializer(companies, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'])
    def generate_data(self, request):
        """Generate random company data"""
        try:
            count = int(request.data.get('count', 5))
            
            # Define possible values
            company_names = ['Company A', 'Company B', 'Company C', 'Company D', 'Company E']
            countries = ['USA', 'Canada', 'UK', 'Australia', 'India']
            
            # Generate companies
            companies = []
            for _ in range(count):
                company = Company.objects.create(
                    name=random.choice(company_names),
                    revenue=random.uniform(20000, 150000),
                    profit=random.uniform(50000, 300000),
                    employees=random.randint(20, 100),
                    country=random.choice(countries)
                )
                companies.append(company)
            
            serializer = self.get_serializer(companies, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'])
    def chart_data(self, request):
        """Get aggregated data for various charts"""
        companies = Company.objects.all()
        
        if not companies:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        
        # Basic company data
        company_data = self.get_serializer(companies, many=True).data
        
        # Aggregate by country
        countries = set(company.country for company in companies)
        country_data = {}
        
        for country in countries:
            country_companies = companies.filter(country=country)
            country_data[country] = {
                'company_count': country_companies.count(),
                'total_revenue': float(country_companies.aggregate(Sum('revenue'))['revenue__sum'] or 0),
                'total_profit': float(country_companies.aggregate(Sum('profit'))['profit__sum'] or 0),
                'total_employees': country_companies.aggregate(Sum('employees'))['employees__sum'] or 0,
            }
        
        # High revenue companies (revenue > 20k)
        high_revenue_companies = companies.filter(revenue__gt=20000)
        high_revenue_data = self.get_serializer(high_revenue_companies, many=True).data
        
        # Heatmap data
        heatmap_data = []
        for company in companies:
            heatmap_data.append({
                'name': company.name,
                'country': company.country,
                'revenue': float(company.revenue),
                'profit': float(company.profit),
                'employees': company.employees,
            })
        
        response_data = {
            'companies': company_data,
            'country_data': country_data,
            'high_revenue_companies': high_revenue_data,
            'heatmap_data': heatmap_data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
