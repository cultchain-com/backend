# Generated by Django 4.2.6 on 2023-10-29 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Committee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('committee_id', models.BigIntegerField(unique=True)),
                ('total_members', models.PositiveIntegerField()),
                ('yes_votes', models.PositiveIntegerField(default=0)),
                ('no_votes', models.PositiveIntegerField(default=0)),
                ('final_decision', models.BooleanField(blank=True, null=True)),
                ('committee_type', models.CharField(choices=[('Event', 'Event'), ('Milestone', 'Milestone'), ('Validator', 'Validator')], max_length=10)),
                ('milestone_index', models.PositiveIntegerField(default=0)),
                ('committee_type_id', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Committee',
                'verbose_name_plural': 'Committees',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('target_amount', models.BigIntegerField()),
                ('end_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(null=True)),
                ('collected_amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('rating_sum', models.BigIntegerField()),
                ('rating_count', models.BigIntegerField()),
                ('category', models.CharField(choices=[('Health', 0), ('Education', 1), ('Environment', 2), ('DisasterRelief', 3), ('AnimalWelfare', 4), ('Others', 5)], max_length=50)),
                ('status', models.CharField(choices=[('PENDING', 0), ('APPROVED', 1), ('REJECTED', 2), ('NOT_STARTED_YET', 3)], max_length=50)),
                ('committee_id', models.BigIntegerField()),
                ('is_fundraising_over', models.BooleanField()),
                ('token_uri', models.URLField(null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('timestamp', models.DateTimeField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='indexer.event')),
            ],
        ),
        migrations.CreateModel(
            name='ValidatorRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staking_amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('reputation_score', models.PositiveIntegerField()),
                ('ipfs_hash', models.CharField(max_length=46)),
                ('validation_status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], max_length=10)),
                ('committee_id', models.PositiveIntegerField()),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='indexer.event')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('milestone_index', models.BigIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('spended_amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('target_amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('end_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(null=True)),
                ('rating_sum', models.BigIntegerField()),
                ('rating_count', models.BigIntegerField()),
                ('committee_id', models.BigIntegerField()),
                ('completed', models.BooleanField()),
                ('is_fund_released', models.BooleanField()),
                ('status', models.CharField(choices=[('PENDING', 0), ('APPROVED', 1), ('REJECTED', 2), ('NOT_STARTED_YET', 3)], max_length=50)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='indexer.event')),
            ],
            options={
                'unique_together': {('event', 'milestone_index')},
            },
        ),
        migrations.CreateModel(
            name='FundRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('release_type', models.CharField(choices=[('Creator', 'Creator'), ('Validator', 'Validator'), ('Platform', 'Platform')], max_length=10)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='indexer.event')),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='EventFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='indexer.event')),
                ('feedback_provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('timestamp', models.DateTimeField()),
                ('message', models.TextField()),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='indexer.event')),
            ],
        ),
        migrations.CreateModel(
            name='CommitteeMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_voted', models.BooleanField(default=False)),
                ('decision', models.BooleanField(default=False)),
                ('feedback', models.TextField(blank=True)),
                ('committee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='indexer.committee')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
            options={
                'unique_together': {('committee', 'member')},
            },
        ),
        migrations.AddField(
            model_name='committee',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='indexer.event'),
        ),
        migrations.AddField(
            model_name='committee',
            name='members',
            field=models.ManyToManyField(related_name='committees', through='indexer.CommitteeMembership', to='user_profile.userprofile'),
        ),
        migrations.AddField(
            model_name='committee',
            name='milestone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='indexer.milestone'),
        ),
    ]
