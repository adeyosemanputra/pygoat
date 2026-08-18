from collections import OrderedDict

from challenge.models import LabCategoryMapping


# Defines the order and metadata for each sidebar category section.
SIDEBAR_CATEGORY_META = [
    ('owasp_2025', 'OWASP TOP 10 2025', 'OWASP10_2025', 'owasp10_2025'),
    ('owasp_2021', 'OWASP TOP 10 2021', 'OWASP10_2021', 'owasp10_2021'),
    ('owasp_2017', 'OWASP TOP 10 2017', 'OWASP10_2017', 'owasp10_2017'),
    ('challenges', 'Challenges', 'challengeSubmenu', 'challengeMenu'),
]


def sidebar_labs(request):
    """Inject structured lab data into all templates for sidebar rendering."""
    mappings = LabCategoryMapping.objects.select_related('lab').order_by(
        'category', 'sort_order'
    )

    sidebar_data = []
    for cat_key, cat_label, collapse_id, menu_id in SIDEBAR_CATEGORY_META:
        cat_mappings = [m for m in mappings if m.category == cat_key]
        if not cat_mappings:
            continue

        # Group by subcategory, preserving insertion order
        subcategories = OrderedDict()
        top_level = []
        for m in cat_mappings:
            entry = {
                'lab_name': m.lab.name,
                'display_name': m.display_name,
                'overview_url_name': m.overview_url_name,
            }
            if m.subcategory:
                subcategories.setdefault(m.subcategory, []).append(entry)
            else:
                top_level.append(entry)

        sidebar_data.append({
            'key': cat_key,
            'label': cat_label,
            'collapse_id': collapse_id,
            'menu_id': menu_id,
            'labs': top_level,
            'subcategories': [
                {'name': sub_name, 'labs': sub_labs}
                for sub_name, sub_labs in subcategories.items()
            ],
        })

    return {'sidebar_categories': sidebar_data}
