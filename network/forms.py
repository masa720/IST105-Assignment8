from django import forms

class NetworkForm(forms.Form):
    mac_address = forms.CharField(label='MAC Address')
    dhcp_version = forms.ChoiceField(
        choices=[('DHCPv4', 'DHCPv4'), ('DHCPv6', 'DHCPv6')]
    )
