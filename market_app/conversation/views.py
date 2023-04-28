from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from item.models import Item
from .forms import ConversationMessageForm
from .models import Conversation

# Create your views here.
@login_required
def new_conversation(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)

    if item.created_by == request.user:
        return redirect('dashboard:index')
    
    converstaions = Conversation.objects.filter(item=item).filter(members__in=[request.user.id])

    if converstaions:
        return redirect('conversation:detail', pk=converstaions.first().id)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)
        
        if form.is_valid():
            converstaion = Conversation.objects.create(item=item)
            converstaion.members.add(request.user)
            converstaion.members.add(item.created_by)
            converstaion.save()

            conversation_message = form.save(commit=False)
            conversation_message.conversation = converstaion
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('item:detail', pk=item_pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/new.html', {
        'form': form,
    })

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations,
    })

@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            converstaion_message= form.save(commit=False)
            converstaion_message.conversation = conversation
            converstaion_message.created_by = request.user
            converstaion_message.save()

            conversation.save()

            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/detail.html', {
        'conversation': conversation,
        'form': form,
    })