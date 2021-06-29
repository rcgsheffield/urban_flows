SELECT
     reading_categories.id
    ,reading_categories.name
    ,reading_types.id
    ,reading_types.name
FROM portal.reading_categories
LEFT JOIN portal.reading_category_reading_type ON reading_categories.id = reading_category_reading_type.reading_category_id
LEFT JOIN portal.reading_types ON reading_category_reading_type.reading_type_id = reading_types.id
ORDER BY 1, 2;

-- DELETE FROM portal.reading_category_reading_type;