def metadata_object(fqname, display_name, api_name, **kwargs):
    kwargs['fullyQualifiedName'] = fqname
    kwargs['label'] = display_name
    kwargs['name'] = api_name

    return kwargs


def metadata_text_field(fqname, display_name, api_name, **kwargs):
    kwargs['type'] = 'Text'
    return metadata_object(fqname, display_name, api_name, **kwargs)


def metadata_numeric_field(fqname, display_name, api_name, precision, scale=2, **kwargs):
    kwargs['type'] = 'Numeric'
    kwargs['precision'] = precision
    kwargs['scale'] = scale
    if 'format' not in kwargs:
        kwargs['format'] = '0.' + '#' * scale

    return metadata_object(fqname, display_name, api_name, **kwargs)


def metadata_date_field(fqname, display_name, api_name, date_format="yyyy-MM-dd", **kwargs):
    kwargs['type'] = 'Date'
    kwargs['format'] = date_format
    return metadata_object(fqname, display_name, api_name, **kwargs)


class DataImporter(object):
    def metadata_schema(self):
        """
            Returns a dict describing an object and its fields
        """
        raise NotImplementedError
