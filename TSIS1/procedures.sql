CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE name ILIKE p_contact_name LIMIT 1;
    IF v_id IS NULL THEN RAISE EXCEPTION 'Contact not found'; END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END;
$$;
 
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE v_contact_id INTEGER; v_group_id INTEGER;
BEGIN
    INSERT INTO groups (name) VALUES (p_group_name) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    SELECT id INTO v_contact_id FROM contacts WHERE name ILIKE p_contact_name LIMIT 1;
    IF v_contact_id IS NULL THEN RAISE EXCEPTION 'Contact not found'; END IF;
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;
 
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (contact_id INTEGER, name VARCHAR, email VARCHAR, birthday DATE, group_name VARCHAR, phone VARCHAR, phone_type VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, c.birthday, g.name, ph.phone, ph.type
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR ph.phone ILIKE '%' || p_query || '%';
END;
$$;
 
CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE (contact_id INTEGER, name VARCHAR, email VARCHAR, birthday DATE, group_name VARCHAR, phone VARCHAR, phone_type VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, c.birthday, g.name, ph.phone, ph.type
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    ORDER BY c.name
    LIMIT p_limit OFFSET p_offset;
END;
$$;