import datetime
import math
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from django.contrib.auth.models import User

from .forms import BudgetForm, EntryForm, ProfitForm
from .models import Budget, Entry, Profit


def _start_of_week(d):
    return d - timedelta(days=d.weekday())  # Monday start


def _period_start(period, today):
    if period == 'daily':
        return today
    if period == 'monthly':
        return today.replace(day=1)
    return _start_of_week(today)  # weekly (default)


@login_required
def entry_view(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('entry')
    else:
        form = EntryForm(initial={'date': date.today()})

    recent = Entry.objects.filter(user=request.user)[:5]
    return render(request, 'ledger/entry_form.html', {'form': form, 'recent': recent})


@login_required
def weekly_view(request):
    entries = Entry.objects.filter(user=request.user)
    weeks = {}
    for e in entries:
        wk_start = _start_of_week(e.date)
        weeks.setdefault(wk_start, []).append(e)

    week_list = []
    for wk_start in sorted(weeks.keys(), reverse=True):
        items = weeks[wk_start]
        wk_end = wk_start + timedelta(days=6)
        week_list.append({
            'label': f"{wk_start.strftime('%b %d')} - {wk_end.strftime('%b %d')}",
            'total': sum(i.cost for i in items),
            'items': sorted(items, key=lambda i: i.date, reverse=True),
            'month': wk_start.month,
        })

    return render(request, 'ledger/weekly.html', {'weeks': week_list})


@login_required
def dashboard_view(request):
    today = date.today()
    budget = Budget.objects.filter(user=request.user).first()

    if budget:
        period_start = _period_start(budget.period, today)
    else:
        period_start = _start_of_week(today)

    period_entries = Entry.objects.filter(user=request.user, date__gte=period_start)
    spent = period_entries.aggregate(total=Sum('cost'))['total'] or 0
    remaining = (budget.amount - spent) if budget else None

    all_entries = Entry.objects.filter(user=request.user)
    most_expensive_list = list(all_entries.order_by('-cost')[:3])

    desc_counts = Counter(e.description.strip().lower() for e in all_entries)
    most_frequent_list = desc_counts.most_common(3)

    donut = None
    if budget and budget.amount:
        pct = float(spent) / float(budget.amount) * 100
        pct_capped = min(pct, 100)
        radius = 70
        circumference = 2 * math.pi * radius
        dash_filled = circumference * pct_capped / 100
        donut = {
            'pct': int(round(pct)),
            'dash_filled': round(dash_filled, 2),
            'circumference': round(circumference, 2),
            'over': pct > 100,
        }

    period_label = {'daily': 'day', 'weekly': 'week', 'monthly': 'month'}.get(
        budget.period if budget else 'weekly', 'week'
    )

    range_start = request.GET.get('start')
    range_end = request.GET.get('end')
    range_total = None
    if range_start or range_end:
        range_qs = all_entries
        if range_start:
            range_qs = range_qs.filter(date__gte=range_start)
        if range_end:
            range_qs = range_qs.filter(date__lte=range_end)
        range_total = range_qs.aggregate(total=Sum('cost'))['total'] or 0

    if request.method == 'POST':
        budget_form = BudgetForm(request.POST, instance=budget)
        if budget_form.is_valid():
            b = budget_form.save(commit=False)
            b.user = request.user
            b.save()
            return redirect('dashboard')
    else:
        budget_form = BudgetForm(instance=budget)

    return render(request, 'ledger/dashboard.html', {
        'budget': budget,
        'spent': spent,
        'remaining': remaining,
        'most_expensive_list': most_expensive_list,
        'most_frequent_list': most_frequent_list,
        'budget_form': budget_form,
        'donut': donut,
        'period_label': period_label,
        'range_start': range_start or '',
        'range_end': range_end or '',
        'range_total': range_total,
    })


@login_required
def income_view(request):
    if request.method == 'POST':
        form = ProfitForm(request.POST)
        if form.is_valid():
            profit = form.save(commit=False)
            profit.user = request.user
            profit.save()
            return redirect('income')
    else:
        form = ProfitForm(initial={'date': date.today()})

    start = request.GET.get('start')
    end = request.GET.get('end')

    profits = Profit.objects.filter(user=request.user)
    entries = Entry.objects.filter(user=request.user)
    if start:
        profits = profits.filter(date__gte=start)
        entries = entries.filter(date__gte=start)
    if end:
        profits = profits.filter(date__lte=end)
        entries = entries.filter(date__lte=end)

    total_profit = profits.aggregate(total=Sum('amount'))['total'] or 0
    total_spent = entries.aggregate(total=Sum('cost'))['total'] or 0
    net = total_profit - total_spent

    return render(request, 'ledger/income.html', {
        'form': form,
        'profits': profits[:20],
        'total_profit': total_profit,
        'total_spent': total_spent,
        'net': net,
        'start': start or '',
        'end': end or '',
    })


@login_required
def entry_edit_view(request, pk):
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    if request.method == 'POST':
        if request.POST.get('delete'):
            entry.delete()
            return redirect('weekly')
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('weekly')
    else:
        form = EntryForm(instance=entry)
    return render(request, 'ledger/edit_entry.html', {'form': form, 'entry': entry})


@login_required
def profit_edit_view(request, pk):
    profit = get_object_or_404(Profit, pk=pk, user=request.user)
    if request.method == 'POST':
        if request.POST.get('delete'):
            profit.delete()
            return redirect('income')
        form = ProfitForm(request.POST, instance=profit)
        if form.is_valid():
            form.save()
            return redirect('income')
    else:
        form = ProfitForm(instance=profit)
    return render(request, 'ledger/edit_profit.html', {'form': form, 'profit': profit})


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('entry')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('entry')
    else:
        form = AuthenticationForm()
    return render(request, 'ledger/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@never_cache
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('entry')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            return redirect('entry')
    else:
        form = UserCreationForm()
    return render(request, 'ledger/signup.html', {'form': form})


import csv
import io
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def import_view(request):
    result = None
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        username = request.POST.get('username', '').strip()
        year_str = request.POST.get('year', '').strip()
        negate = request.POST.get('negate') == 'on'

        try:
            target_user = User.objects.get(username=username)
            year = int(year_str)
            decoded = csv_file.read().decode('utf-8')
            reader = csv.reader(io.StringIO(decoded))
            next(reader, None)
            created = 0
            skipped = 0
            last_date = None
            current_year = year
            last_month = None
            for row in reader:
                if len(row) < 5:
                    skipped += 1
                    continue
                date_str, desc, cost_str = row[2], row[3], row[4]
                desc_clean = desc.strip()
                if not desc_clean or desc_clean.lower() in {'total', 'amount remaining'}:
                    skipped += 1
                    continue
                parsed = None
                v = date_str.strip()
                if v:
                    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
                        try:
                            parsed = datetime.datetime.strptime(v, fmt).date()
                            break
                        except ValueError:
                            continue
                    if parsed is None:
                        try:
                            md = datetime.datetime.strptime(v, '%m/%d')
                            if last_month is not None and md.month < last_month:
                                current_year += 1
                            parsed = datetime.date(current_year, md.month, md.day)
                            last_month = md.month
                        except ValueError:
                            pass
                if parsed is not None:
                    last_date = parsed
                entry_date = parsed or last_date
                if entry_date is None:
                    skipped += 1
                    continue
                try:
                    cost = Decimal(cost_str.strip())
                    if negate:
                        cost = -cost
                except (InvalidOperation, AttributeError):
                    skipped += 1
                    continue
                Entry.objects.create(user=target_user, date=entry_date, description=desc_clean, cost=cost)
                created += 1
            result = f'Imported {created} entries, skipped {skipped} rows.'
        except User.DoesNotExist:
            result = f'No user "{username}" found.'
        except ValueError:
            result = 'Year must be a number.'
        except Exception as e:
            result = f'Error: {e}'
    return render(request, 'ledger/import_csv.html', {'result': result})
