from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from .models import Project, Skill, Resume, ContactMessage
from .forms import ContactForm

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = Project.objects.filter(
            is_featured=True, 
            is_active=True
        ).order_by('display_order')[:3]
        context['skills'] = Skill.objects.filter(
            is_active=True
        ).order_by('category', 'display_order')
        context['meta_title'] = "Professional Portfolio"
        context['meta_description'] = "Welcome to my professional portfolio showcasing my skills and projects."
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = "About Me"
        context['meta_description'] = "Learn more about my professional background and skills."
        return context


class ProjectListView(ListView):
    model = Project
    template_name = 'core/projects.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(
            is_active=True
        ).order_by('display_order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = "My Projects"
        context['meta_description'] = "Explore my portfolio of professional projects and work samples."
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'core/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['meta_title'] = f"Project: {project.title}"
        context['meta_description'] = project.short_description
        return context


class ResumeView(TemplateView):
    template_name = 'core/resume.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resume'] = Resume.objects.filter(is_default=True).first()
        context['meta_title'] = "My Resume"
        context['meta_description'] = "Download my professional resume and view my work experience."
        return context


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = "Contact Me"
        context['meta_description'] = "Get in touch with me for professional inquiries or collaborations."
        return context
    
    def form_valid(self, form):
        contact_message = form.save()
        
        # Send email notification
        send_mail(
            subject=f"New Contact Message: {contact_message.subject}",
            message=f"""
            Name: {contact_message.name}
            Email: {contact_message.email}
            Message: {contact_message.message}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
        messages.success(self.request, 'Your message has been sent successfully!')
        return super().form_valid(form)