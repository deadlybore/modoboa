from django import forms
from django.utils.translation import ugettext_lazy
from modoboa.lib.formutils import YesNoField, SeparatorField
from modoboa.lib.sysutils import exec_cmd
from modoboa.lib import parameters


class AdminParametersForm(parameters.AdminParametersForm):
    app = "admin"

    mbsep = SeparatorField(label=ugettext_lazy("Mailboxes"))

    handle_mailboxes = YesNoField(
        label=ugettext_lazy("Handle mailboxes on filesystem"),
        initial="no",
        help_text=ugettext_lazy("Rename or remove mailboxes on the filesystem when they get renamed or removed within Modoboa")
    )

    mailboxes_owner = forms.CharField(
        label=ugettext_lazy("Mailboxes ower"),
        initial="vmail",
        help_text=ugettext_lazy("The UNIX account who owns mailboxes on the filesystem")
    )

    default_domain_quota = forms.IntegerField(
        label=ugettext_lazy("Default domain quota"),
        initial=0,
        help_text=ugettext_lazy(
            "Default quota (in MB) applied to freshly created domains with no "
            "value specified. A value of 0 means no quota."
        ),
        widget=forms.TextInput(attrs={'class': 'span2'})
    )

    auto_account_removal = YesNoField(
        label=ugettext_lazy("Automatic account removal"),
        initial="no",
        help_text=ugettext_lazy("When a mailbox is removed, also remove the associated account")
    )

    # Visibility rules
    visibility_rules = {
        "mailboxes_owner": "handle_mailboxes=yes",
    }

    def __init__(self, *args, **kwargs):
        super(AdminParametersForm, self).__init__(*args, **kwargs)
        hide_fields = False
        try:
            code, version = exec_cmd("dovecot --version")
        except OSError:
            hide_fields = True
        else:
            if code or not version.strip().startswith("2"):
                hide_fields = True
        if hide_fields:
            del self.fields["handle_mailboxes"]
            del self.fields["mailboxes_owner"]

    def clean_default_domain_quota(self):
        """Ensure quota is a positive integer."""
        if self.cleaned_data['default_domain_quota'] < 0:
            raise forms.ValidationError(
                ugettext_lazy('Must be a positive integer')
            )
        return self.cleaned_data['default_domain_quota']
