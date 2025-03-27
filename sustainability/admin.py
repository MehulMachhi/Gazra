from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Avg
from .models import (
    ReplicableProgram, ProgramReplication, CorporatePartner,
    FundingProposal, AnnualBudget, BudgetTracking, FranchiseModel,
    FranchiseLocation, Product, ConsultingService, ConsultingEngagement,
    SocialEnterpriseMetrics, SustainabilityReport
)


@admin.register(AnnualBudget)
class AnnualBudgetAdmin(admin.ModelAdmin):
    list_display = (
        'fiscal_year' , 'total_budget_display' ,
        'budget_breakdown_display' , 'status' ,
        'approval_status'
    )
    list_filter = ('status' , 'fiscal_year')
    search_fields = ('fiscal_year' , 'notes')
    readonly_fields = ('created_at' , 'updated_at')

    fieldsets = (
        ('Basic Information' , {
            'fields': ('fiscal_year' , 'total_budget' , 'status')
        }) ,
        ('Budget Breakdown' , {
            'fields': (
                'staff_salaries' , 'operational_costs' ,
                'program_costs' , 'marketing_costs' ,
                'contingency_fund'
            )
        }) ,
        ('Details' , {
            'fields': ('detailed_breakdown' , 'notes')
        }) ,
        ('Approval' , {
            'fields': ('prepared_by' , 'approved_by')
        })
    )

    def total_budget_display(self , obj):
        return format_html('₹{:,}' , obj.total_budget)

    total_budget_display.short_description = 'Total Budget'

    def budget_breakdown_display(self , obj):
        return format_html(
            'Staff: ₹{:,}<br>'
            'Ops: ₹{:,}<br>'
            'Programs: ₹{:,}' ,
            obj.staff_salaries ,
            obj.operational_costs ,
            obj.program_costs
        )

    budget_breakdown_display.short_description = 'Breakdown'

    def approval_status(self , obj):
        if obj.approved_by:
            return format_html(
                '<span style="color: green;">Approved by {}</span>' ,
                obj.approved_by.user.get_full_name()
            )
        return format_html(
            '<span style="color: orange;">Pending Approval</span>'
        )

    approval_status.short_description = 'Approval'
    
    def has_module_permission(self, request):
        return False

@admin.register(BudgetTracking)
class BudgetTrackingAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'annual_budget' , 'month' , 'category' ,
        'amount_comparison' , 'variance_display' ,
        'recorded_by'
    )
    list_filter = ('month' , 'category' , 'annual_budget')
    search_fields = ('category' , 'variance_explanation')

    def amount_comparison(self , obj):
        return format_html(
            'Budget: ₹{:,}<br>'
            'Actual: ₹{:,}' ,
            obj.budgeted_amount ,
            obj.actual_amount
        )

    amount_comparison.short_description = 'Amount'

    def variance_display(self , obj):
        variance = obj.actual_amount - obj.budgeted_amount
        percentage = (variance / obj.budgeted_amount) * 100
        color = 'red' if variance > 0 else 'green'
        return format_html(
            '<span style="color: {};">₹{:,} ({:+.1f}%)</span>' ,
            color ,
            abs(variance) ,
            percentage
        )

    variance_display.short_description = 'Variance'


@admin.register(FranchiseModel)
class FranchiseModelAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'name' , 'status' , 'setup_cost_display' ,
        'franchise_fee_display' , 'locations_count' ,
        'developed_by'
    )
    list_filter = ('status' ,)
    search_fields = ('name' , 'description' , 'operational_guidelines')
    readonly_fields = ('created_at' , 'updated_at')

    fieldsets = (
        ('Basic Information' , {
            'fields': ('name' , 'description' , 'status')
        }) ,
        ('Guidelines' , {
            'fields': (
                'operational_guidelines' , 'training_modules' ,
                'branding_guidelines'
            )
        }) ,
        ('Financial' , {
            'fields': (
                'setup_cost' , 'revenue_model' ,
                'franchise_fee' , 'royalty_structure'
            )
        }) ,
        ('Support & Legal' , {
            'fields': (
                'support_services' , 'legal_requirements' ,
                'toolkit_documents'
            )
        }) ,
        ('Management' , {
            'fields': ('developed_by' ,)
        })
    )

    def setup_cost_display(self , obj):
        return format_html('₹{:,}' , obj.setup_cost)

    setup_cost_display.short_description = 'Setup Cost'

    def franchise_fee_display(self , obj):
        return format_html('₹{:,}' , obj.franchise_fee)

    franchise_fee_display.short_description = 'Franchise Fee'

    def locations_count(self , obj):
        count = obj.locations.count()
        return format_html(
            '<a href="{}?franchise_model__id={}">{} locations</a>' ,
            reverse('admin:sustainability_franchiselocation_changelist') ,
            obj.id ,
            count
        )

    locations_count.short_description = 'Locations'


@admin.register(FranchiseLocation)
class FranchiseLocationAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'location_name' , 'franchise_model' , 'status' ,
        'revenue_display' , 'employees_count' , 'launch_date'
    )
    list_filter = ('status' , 'launch_date' , 'franchise_model')
    search_fields = ('location_name' , 'partner_organization' , 'address')
    readonly_fields = ('created_at' , 'updated_at')

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'franchise_model' , 'location_name' ,
                'partner_organization' , 'address'
            )
        }) ,
        ('Operations' , {
            'fields': (
                'launch_date' , 'status' , 'employees_count' ,
                'monthly_revenue'
            )
        }) ,
        ('Performance' , {
            'fields': ('performance_metrics' , 'feedback')
        }) ,
        ('Support' , {
            'fields': ('mentor' ,)
        })
    )

    def revenue_display(self , obj):
        return format_html('₹{:,}/month' , obj.monthly_revenue)

    revenue_display.short_description = 'Monthly Revenue'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'name' , 'product_type' , 'price_display' ,
        'margin_display' , 'stock_quantity' , 'is_active'
    )
    list_filter = ('product_type' , 'is_active')
    search_fields = ('name' , 'description')
    readonly_fields = ('created_at' , 'updated_at')

    def price_display(self , obj):
        return format_html(
            'SP: ₹{:,}<br>CP: ₹{:,}' ,
            obj.price ,
            obj.cost_price
        )

    price_display.short_description = 'Price'

    def margin_display(self , obj):
        margin = obj.price - obj.cost_price
        margin_percentage = (margin / obj.price) * 100
        return format_html(
            '₹{:,} ({:.1f}%)' ,
            margin ,
            margin_percentage
        )

    margin_display.short_description = 'Margin'



@admin.register(ConsultingService)
class ConsultingServiceAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'title' , 'service_type_display' , 'price_display' ,
        'duration' , 'consultant_name' , 'active_status'
    )
    list_filter = (
        ('service_type' , admin.ChoicesFieldListFilter) ,
        ('is_active' , admin.BooleanFieldListFilter)
    )
    search_fields = ('title' , 'description' , 'deliverables')

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'title' , 'service_type' , 'description' ,
                'duration' , 'price'
            )
        }) ,
        ('Service Details' , {
            'fields': (
                'deliverables' , 'target_audience' ,
                'prerequisites' , 'materials_included'
            )
        }) ,
        ('Management' , {
            'fields': (
                'consultant' , 'is_active'
            )
        })
    )

    def service_type_display(self , obj):
        return obj.get_service_type_display()

    service_type_display.short_description = 'Service Type'

    def price_display(self , obj):
        return format_html('₹{:,}' , obj.price)

    price_display.short_description = 'Price'

    def consultant_name(self , obj):
        return obj.consultant.user.get_full_name()

    consultant_name.short_description = 'Consultant'

    def active_status(self , obj):
        return format_html(
            '<span style="color: {};">{}</span>' ,
            'green' if obj.is_active else 'red' ,
            'Active' if obj.is_active else 'Inactive'
        )

    active_status.short_description = 'Status'

    def get_queryset(self , request):
        return super().get_queryset(request).select_related(
            'consultant' ,
            'consultant__user'
        )


# sustainability/admin.py (continued)

@admin.register(ConsultingEngagement)
class ConsultingEngagementAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'service' , 'client_organization' , 'status' ,
        'contract_value_display' , 'payment_status' ,
        'satisfaction_display'
    )
    list_filter = (
        'status' , 'payment_status' , 'start_date' ,
        'service'
    )
    search_fields = (
        'client_name' , 'client_organization' ,
        'feedback'
    )
    readonly_fields = ('created_at' , 'updated_at')

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'service' , 'client_name' ,
                'client_organization' , 'consultant'
            )
        }) ,
        ('Timeline' , {
            'fields': (
                'start_date' , 'end_date' , 'status'
            )
        }) ,
        ('Financial' , {
            'fields': (
                'contract_value' , 'payment_status' ,
                'contract_document'
            )
        }) ,
        ('Deliverables & Feedback' , {
            'fields': (
                'deliverables_status' , 'feedback' ,
                'satisfaction_rating'
            )
        })
    )

    def contract_value_display(self , obj):
        return format_html('₹{:,}' , obj.contract_value)

    contract_value_display.short_description = 'Contract Value'

    def satisfaction_display(self , obj):
        if obj.satisfaction_rating:
            stars = '★' * obj.satisfaction_rating + '☆' * (5 - obj.satisfaction_rating)
            return format_html(
                '<span style="color: gold;">{}</span>' ,
                stars
            )
        return '-'

    satisfaction_display.short_description = 'Satisfaction'


@admin.register(SocialEnterpriseMetrics)
class SocialEnterpriseMetricsAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'report_date' , 'metric_type' , 'revenue_summary' ,
        'impact_summary' , 'recorded_by'
    )
    list_filter = ('metric_type' , 'report_date')
    readonly_fields = ('created_at' ,)

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'metric_type' , 'report_date' , 'recorded_by'
            )
        }) ,
        ('Product Metrics' , {
            'fields': (
                'total_product_revenue' , 'total_products_sold' ,
                'best_selling_products'
            )
        }) ,
        ('Consulting Metrics' , {
            'fields': (
                'consulting_revenue' , 'engagements_completed' ,
                'client_satisfaction'
            )
        }) ,
        ('Franchise Metrics' , {
            'fields': (
                'franchise_revenue' , 'active_franchises' ,
                'franchise_performance'
            )
        }) ,
        ('Impact Metrics' , {
            'fields': (
                'jobs_created' , 'beneficiaries_impacted' ,
                'social_return'
            )
        }) ,
        ('Additional Information' , {
            'fields': ('notes' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def revenue_summary(self , obj):
        total_revenue = (
                obj.total_product_revenue +
                obj.consulting_revenue +
                obj.franchise_revenue
        )
        return format_html(
            'Total: ₹{:,}<br>'
            'Products: ₹{:,}<br>'
            'Consulting: ₹{:,}<br>'
            'Franchise: ₹{:,}' ,
            total_revenue ,
            obj.total_product_revenue ,
            obj.consulting_revenue ,
            obj.franchise_revenue
        )

    revenue_summary.short_description = 'Revenue Summary'

    def impact_summary(self , obj):
        return format_html(
            'Jobs: {}<br>'
            'Beneficiaries: {}' ,
            obj.jobs_created ,
            obj.beneficiaries_impacted
        )

    impact_summary.short_description = 'Impact Summary'


@admin.register(SustainabilityReport)
class SustainabilityReportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'report_type' , 'period_display' , 'financial_summary' ,
        'impact_summary' , 'status' , 'prepared_by'
    )
    list_filter = ('report_type' , 'status' , 'period_start')
    search_fields = (
        'growth_projections' , 'sustainability_initiatives' ,
        'risk_assessment'
    )
    readonly_fields = ('created_at' , 'updated_at')

    fieldsets = (
        ('Report Information' , {
            'fields': (
                'report_type' , 'period_start' , 'period_end' ,
                'status'
            )
        }) ,
        ('Financial Sustainability' , {
            'fields': (
                'revenue_streams' , 'total_revenue' ,
                'total_expenses' , 'financial_sustainability_ratio'
            )
        }) ,
        ('Program Sustainability' , {
            'fields': (
                'active_programs' , 'program_metrics' ,
                'replication_status'
            )
        }) ,
        ('Partnership & Impact' , {
            'fields': (
                'active_partnerships' , 'partnership_value' ,
                'partner_satisfaction' , 'beneficiaries_reached' ,
                'impact_metrics' , 'community_feedback'
            )
        }) ,
        ('Future Planning' , {
            'fields': (
                'growth_projections' , 'sustainability_initiatives' ,
                'risk_assessment'
            )
        }) ,
        ('Documentation' , {
            'fields': (
                'prepared_by' , 'report_file'
            )
        })
    )

    def period_display(self , obj):
        return f"{obj.period_start} to {obj.period_end}"

    period_display.short_description = 'Period'

    def financial_summary(self , obj):
        return format_html(
            'Revenue: ₹{:,}<br>'
            'Expenses: ₹{:,}<br>'
            'Ratio: {:.2f}' ,
            obj.total_revenue ,
            obj.total_expenses ,
            obj.financial_sustainability_ratio
        )

    financial_summary.short_description = 'Financial Summary'

    def impact_summary(self , obj):
        return format_html(
            'Programs: {}<br>'
            'Partnerships: {}<br>'
            'Beneficiaries: {}' ,
            obj.active_programs ,
            obj.active_partnerships ,
            obj.beneficiaries_reached
        )

    impact_summary.short_description = 'Impact Summary'

    def save_model(self , request , obj , form , change):
        if not change:  # If creating new object
            obj.prepared_by = request.user.member
        super().save_model(request , obj , form , change)




# Register any additional admin customizations here
admin.site.site_header = 'MCSU Sustainability Management'
admin.site.site_title = 'MCSU Sustainability'
admin.site.index_title = 'Sustainability Management System'