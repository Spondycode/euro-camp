import csv
import io
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from .models import Campsite, Product


def approve_campsites(modeladmin, request, queryset):
    """Admin action to approve selected campsites."""
    updated = queryset.update(is_approved=True)
    modeladmin.message_user(request, f'{updated} campsite(s) approved.')
approve_campsites.short_description = "Approve selected campsites"


def reject_campsites(modeladmin, request, queryset):
    """Admin action to reject (delete) selected campsites."""
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f'{count} campsite(s) rejected and deleted.')
reject_campsites.short_description = "Reject and delete selected campsites"


@admin.register(Campsite)
class CampsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_approved', 'is_premium', 'suggested_by', 'created_by', 'created_at')
    list_filter = ('is_approved', 'is_premium', 'country', 'created_at')
    search_fields = ('name', 'country', 'description', 'suggested_by__username')
    ordering = ('name',)
    actions = [approve_campsites, reject_campsites]
    list_editable = ('is_premium',)
    
    readonly_fields = ('created_at', 'updated_at')
    change_list_template = 'admin/core/campsite/change_list.html'
    
    def get_urls(self):
        """Add custom URL for CSV import."""
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='core_campsite_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv(self, request):
        """Handle CSV import for campsites."""
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a CSV file to upload.')
                return redirect('..')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV file.')
                return redirect('..')
            
            try:
                # Read CSV file
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                created_count = 0
                error_rows = []
                
                for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                    try:
                        # Validate required fields
                        required_fields = ['name', 'town', 'description', 'map_location', 'country']
                        missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
                        
                        if missing_fields:
                            error_rows.append(f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}")
                            continue
                        
                        # Validate country code
                        country_code = row['country'].strip().upper()
                        valid_countries = dict(Campsite.COUNTRY_CHOICES)
                        if country_code not in valid_countries:
                            error_rows.append(f"Row {row_num}: Invalid country code '{country_code}'")
                            continue
                        
                        # Create campsite
                        campsite = Campsite(
                            name=row['name'].strip(),
                            town=row['town'].strip(),
                            description=row['description'].strip(),
                            map_location=row['map_location'].strip(),
                            country=country_code,
                            website=row.get('website', '').strip(),
                            phone_number=row.get('phone_number', '').strip(),
                            image_url=row.get('image_url', '').strip() or None,
                            is_approved=row.get('is_approved', '').strip().lower() in ['true', '1', 'yes'],
                            is_premium=row.get('is_premium', '').strip().lower() in ['true', '1', 'yes'],
                            created_by=request.user,
                        )
                        campsite.save()
                        created_count += 1
                        
                    except Exception as e:
                        error_rows.append(f"Row {row_num}: {str(e)}")
                
                # Show results
                if created_count > 0:
                    messages.success(request, f'Successfully imported {created_count} campsite(s).')
                
                if error_rows:
                    error_message = 'Errors encountered:\n' + '\n'.join(error_rows[:10])  # Show first 10 errors
                    if len(error_rows) > 10:
                        error_message += f'\n... and {len(error_rows) - 10} more errors'
                    messages.warning(request, error_message)
                
                return redirect('..')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect('..')
        
        # GET request - show upload form
        return render(request, 'admin/core/campsite/import_csv.html', {
            'title': 'Import Campsites from CSV',
            'country_choices': Campsite.COUNTRY_CHOICES,
        })


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'created_by', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_featured',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
