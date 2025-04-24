# Import necessary modules from Django
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView

# Import models and forms specific to this project
from .models import Project, Skill, Resume, ContactMessage
from .forms import ContactForm

# Home page view displaying featured projects and skills
class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the featured projects (limited to 3)
        context['featured_projects'] = Project.objects.filter(
            is_featured=True, 
            is_active=True
        ).order_by('display_order')[:3]

        # Fetch all active skills categorized and ordered
        context['skills'] = Skill.objects.filter(
            is_active=True
        ).order_by('category', 'display_order')

        # SEO-related meta tags
        context['meta_title'] = "Professional Portfolio"
        context['meta_description'] = "Welcome to my professional portfolio showcasing my skills and projects."

        return context

# About page view to display personal information
class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # SEO-related meta tags
        context['meta_title'] = "About Me"
        context['meta_description'] = "Learn more about my professional background and skills."

        return context

# View to list all active projects
class ProjectListView(ListView):
    model = Project
    template_name = 'core/projects.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        # Retrieve only active projects and order by display preference
        return Project.objects.filter(
            is_active=True
        ).order_by('display_order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # SEO-related meta tags
        context['meta_title'] = "My Projects"
        context['meta_description'] = "Explore my portfolio of professional projects and work samples."

        return context

# Detailed view of a single project
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'core/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch project details
        project = self.get_object()

        # SEO-related meta tags dynamically set based on project information
        context['meta_title'] = f"Project: {project.title}"
        context['meta_description'] = project.short_description

        return context

# Resume page view to showcase or provide resume download option
class ResumeView(TemplateView):
    template_name = 'core/resume.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the default resume (only one resume marked as default)
        context['resume'] = Resume.objects.filter(is_default=True).first()

        # SEO-related meta tags
        context['meta_title'] = "My Resume"
        context['meta_description'] = "Download my professional resume and view my work experience."

        return context

# Contact page view with a form to send inquiries
class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact/'  # Redirect URL on successful form submission
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # SEO-related meta tags
        context['meta_title'] = "Contact Me"
        context['meta_description'] = "Get in touch with me for professional inquiries or collaborations."

        return context
    
    def form_valid(self, form):
        # Save contact message submitted via the form
        contact_message = form.save()
        
        # Send email notification to admin using Django's email system
        send_mail(
            subject=f"New Contact Message: {contact_message.subject}",
            message=f"""
            Name: {contact_message.name}
            Email: {contact_message.email}
            Message: {contact_message.message}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,  # Ensures errors in email sending are reported
        )
        
        # Show success message after form submission
        messages.success(self.request, 'Your message has been sent successfully!')
        
        return super().form_valid(form)
