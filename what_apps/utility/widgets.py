from django import forms
from django.forms.widgets import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.simplejson import JSONEncoder

class JQueryAutoComplete(forms.TextInput):
    def __init__(self, source, options={}, attrs={}):
        """source can be a list containing the autocomplete values or a
        string containing the url used for the XHR request.
        
        For available options see the autocomplete sample page::
        http://jquery.bassistance.de/autocomplete/"""
        
        self.options = None
        self.attrs = {'autocomplete': 'off'}
        self.source = source
        if len(options) > 0:
            self.options = JSONEncoder().encode(options)
        
        self.attrs.update(attrs)
    
    def render_js(self, field_id):
        if isinstance(self.source, list):
            source = JSONEncoder().encode(self.source)
        elif isinstance(self.source, str):
            source = "'%s'" % escape(self.source)
        else:
            raise ValueError('source type is not valid')
        
        options = ''
        if self.options:
            options += ',%s' % self.options

        return u'$(\'#%s\').autocomplete(%s%s);' % (field_id, source, options)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            final_attrs['value'] = escape(smart_unicode(value))

        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name    
        
        return u'''<input type="text" %(attrs)s/>
        <script type="text/javascript"><!--//
        %(js)s//--></script>
        ''' % {
            'attrs' : flatatt(final_attrs),
            'js' : self.render_js(final_attrs['id']),
        }



import datetime
import re

from django.forms.widgets import Widget, Select, TextInput
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

__all__ = ('SelectDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class SelectMonthAndDayWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    none_value = (0, '---')
    month_field = '%s_month'
    day_field = '%s_day'

    def __init__(self, attrs=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required

    def render(self, name, value, attrs=None):
        try:
            month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        
        day_choices = [(i, i) for i in range(1, 32)]
        if not (self.required and value):
            day_choices.insert(0, self.none_value)
        local_attrs = self.build_attrs(id=self.day_field % id_)
        
        s = Select(choices=day_choices)
        select_html = s.render(self.day_field % name, day_val, local_attrs)
        output.append(select_html)
            
        month_choices = MONTHS.items()
        if not (self.required and value):
            month_choices.append(self.none_value)
        month_choices.sort()
        local_attrs['id'] = self.month_field % id_
        
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if m and d:
            return '%s-%s' % (m, d)
        return data.get(name, None)
