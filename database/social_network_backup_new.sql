PGDMP     3    &        
        y            social_network_v2    13.2    13.2 G    4           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            5           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            6           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            7           1262    8233908    social_network_v2    DATABASE     f   CREATE DATABASE social_network_v2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';
 !   DROP DATABASE social_network_v2;
                postgres    false                        3079    8233909    pgcrypto 	   EXTENSION     <   CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
    DROP EXTENSION pgcrypto;
                   false            8           0    0    EXTENSION pgcrypto    COMMENT     <   COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
                        false    2            �           1247    8233948    authenticated_user    TYPE     �   CREATE TYPE public.authenticated_user AS (
	id uuid,
	first_name character varying,
	last_name character varying,
	auth_timestamp timestamp without time zone
);
 %   DROP TYPE public.authenticated_user;
       public          social_demo_admin    false            �           1247    8233962    new_post    TYPE     d   CREATE TYPE public.new_post AS (
	user_id uuid,
	image_id uuid,
	content character varying(2048)
);
    DROP TYPE public.new_post;
       public       
   alex_mezga    false            �           1247    8233965    new_room    TYPE     �   CREATE TYPE public.new_room AS (
	owner_id uuid,
	image_id uuid,
	title character varying(32),
	about character varying(1024)
);
    DROP TYPE public.new_room;
       public       
   alex_mezga    false            �           1247    8233968    new_user    TYPE     �   CREATE TYPE public.new_user AS (
	email character varying,
	password_text character varying,
	first_name character varying,
	last_name character varying
);
    DROP TYPE public.new_user;
       public       
   alex_mezga    false            �           1247    8234086    visibility_type    TYPE     \   CREATE TYPE public.visibility_type AS ENUM (
    'public',
    'friends',
    'personal'
);
 "   DROP TYPE public.visibility_type;
       public       
   alex_mezga    false                       1255    8233969    add_follower(uuid, uuid)    FUNCTION     �   CREATE FUNCTION public.add_follower(user_id uuid, follower_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		insert into followers (user_id, follower_id) values (user_id, follower_id);
		return true;
	END;
$$;
 C   DROP FUNCTION public.add_follower(user_id uuid, follower_id uuid);
       public          social_demo_admin    false            9           0    0 5   FUNCTION add_follower(user_id uuid, follower_id uuid)    ACL     c   GRANT ALL ON FUNCTION public.add_follower(user_id uuid, follower_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    271            �            1255    8233971    authenticate_user(text, text)    FUNCTION     �  CREATE FUNCTION public.authenticate_user(email text, password_text text) RETURNS public.authenticated_user
    LANGUAGE plpgsql SECURITY DEFINER
    AS $_$
	DECLARE
		user authenticated_user;
	BEGIN
		select into user.id, user.first_name, user.last_name, user.auth_timestamp 
			id, first_name, last_name, current_timestamp from users 
			where users.email = $1
			and users.password_hash = crypt($2, password_hash);
		return user;
	END;
$_$;
 H   DROP FUNCTION public.authenticate_user(email text, password_text text);
       public          social_demo_admin    false    684                       1255    8233972    create_post(public.new_post)    FUNCTION     '  CREATE FUNCTION public.create_post(post public.new_post) RETURNS uuid
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	DECLARE
		_id uuid;
	BEGIN
		insert into posts (user_id, image_id, content)
		values (post.user_id, post.image_id, post.content) returning id into _id;
		return _id;
	END;
$$;
 8   DROP FUNCTION public.create_post(post public.new_post);
       public          social_demo_admin    false    687            :           0    0 *   FUNCTION create_post(post public.new_post)    ACL     X   GRANT ALL ON FUNCTION public.create_post(post public.new_post) TO social_demo_api_role;
          public          social_demo_admin    false    269                       1255    8233973    create_room(public.new_room)    FUNCTION     8  CREATE FUNCTION public.create_room(room public.new_room) RETURNS uuid
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	DECLARE
		_id uuid;
	BEGIN
		insert into rooms (owner_id, image_id, title, about)
		values (room.owner_id, room.image_id, room.title, room.about) returning id into _id;
		return _id;
	END;
$$;
 8   DROP FUNCTION public.create_room(room public.new_room);
       public          social_demo_admin    false    690            ;           0    0 *   FUNCTION create_room(room public.new_room)    ACL     X   GRANT ALL ON FUNCTION public.create_room(room public.new_room) TO social_demo_api_role;
          public          social_demo_admin    false    270                       1255    8233974    create_user(public.new_user)    FUNCTION     c  CREATE FUNCTION public.create_user(usr public.new_user) RETURNS text
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	DECLARE
		user_id text;
	BEGIN
		insert into public.users (email, password_hash, first_name, last_name) 
		values (usr.email, hash(usr.password_text), usr.first_name, usr.last_name) returning id into user_id;
		return user_id;
	END;
$$;
 7   DROP FUNCTION public.create_user(usr public.new_user);
       public          social_demo_admin    false    693            <           0    0 )   FUNCTION create_user(usr public.new_user)    ACL     W   GRANT ALL ON FUNCTION public.create_user(usr public.new_user) TO social_demo_api_role;
          public          social_demo_admin    false    272                       1255    8233975    delete_image(uuid)    FUNCTION     �   CREATE FUNCTION public.delete_image(image_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		DELETE FROM images WHERE id = image_id;
		return true;
	END;
$$;
 2   DROP FUNCTION public.delete_image(image_id uuid);
       public          social_demo_admin    false            =           0    0 $   FUNCTION delete_image(image_id uuid)    ACL     R   GRANT ALL ON FUNCTION public.delete_image(image_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    261                       1255    8233976    delete_post(uuid)    FUNCTION     �   CREATE FUNCTION public.delete_post(post_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		DELETE FROM posts WHERE id = post_id;
		return true;
	END;
$$;
 0   DROP FUNCTION public.delete_post(post_id uuid);
       public          social_demo_admin    false            >           0    0 "   FUNCTION delete_post(post_id uuid)    ACL     P   GRANT ALL ON FUNCTION public.delete_post(post_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    262                       1255    8233977    delete_room(uuid)    FUNCTION     �   CREATE FUNCTION public.delete_room(room_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		DELETE FROM rooms WHERE id = room_id;
		return true;
	END;
$$;
 0   DROP FUNCTION public.delete_room(room_id uuid);
       public          social_demo_admin    false            ?           0    0 "   FUNCTION delete_room(room_id uuid)    ACL     P   GRANT ALL ON FUNCTION public.delete_room(room_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    263                       1255    8233978    delete_user(uuid)    FUNCTION     �   CREATE FUNCTION public.delete_user(user_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	DECLARE
		_id boolean;
	BEGIN
		DELETE FROM posts WHERE id = user_id;
		return true;
	END;
$$;
 0   DROP FUNCTION public.delete_user(user_id uuid);
       public          social_demo_admin    false            @           0    0 "   FUNCTION delete_user(user_id uuid)    ACL     P   GRANT ALL ON FUNCTION public.delete_user(user_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    264            	           1255    8233979    flush()    FUNCTION     =  CREATE FUNCTION public.flush() RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		DELETE FROM posts WHERE create_timestamp < current_timestamp - interval '1 day';
		DELETE FROM images WHERE is_profile = false AND create_timestamp < current_timestamp - interval '1 day';
		return true;
	END;
$$;
    DROP FUNCTION public.flush();
       public          social_demo_admin    false            A           0    0    FUNCTION flush()    ACL     >   GRANT ALL ON FUNCTION public.flush() TO social_demo_api_role;
          public          social_demo_admin    false    265            
           1255    8233980    get_followers(uuid)    FUNCTION        CREATE FUNCTION public.get_followers(user_id uuid) RETURNS uuid[]
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	DECLARE
		followers uuid[];
	BEGIN
		select follower_id from followers where user_id = user_id into followers;
		return followers;
	END;
$$;
 2   DROP FUNCTION public.get_followers(user_id uuid);
       public          social_demo_admin    false            B           0    0 $   FUNCTION get_followers(user_id uuid)    ACL     R   GRANT ALL ON FUNCTION public.get_followers(user_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    266                       1255    8233981 
   hash(text)    FUNCTION     �   CREATE FUNCTION public.hash(str text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
	BEGIN
		RETURN crypt($1, gen_salt('bf', 8));
	END;
$_$;
 %   DROP FUNCTION public.hash(str text);
       public          social_demo_admin    false                       1255    8233982    join_room(uuid, uuid, boolean)    FUNCTION     @  CREATE FUNCTION public.join_room(_user uuid, _room uuid, _admin boolean) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		insert into room_users (user_id, room_id, is_admin)
		values (_user, _room, _admin)
		on conflict(user_id, room_id) do update set is_admin = _admin;
		return true;
	END;
$$;
 H   DROP FUNCTION public.join_room(_user uuid, _room uuid, _admin boolean);
       public          social_demo_admin    false            C           0    0 :   FUNCTION join_room(_user uuid, _room uuid, _admin boolean)    ACL     h   GRANT ALL ON FUNCTION public.join_room(_user uuid, _room uuid, _admin boolean) TO social_demo_api_role;
          public          social_demo_admin    false    267            �            1255    8233983    leave_room(uuid, uuid)    FUNCTION     �   CREATE FUNCTION public.leave_room(_user uuid, _room uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		DELETE FROM room_users WHERE user_id = user AND room_id = room;
		return true;
	END;
$$;
 9   DROP FUNCTION public.leave_room(_user uuid, _room uuid);
       public          social_demo_admin    false            D           0    0 +   FUNCTION leave_room(_user uuid, _room uuid)    ACL     Y   GRANT ALL ON FUNCTION public.leave_room(_user uuid, _room uuid) TO social_demo_api_role;
          public          social_demo_admin    false    247            �            1255    8233984    remove_follower(uuid, uuid)    FUNCTION     �   CREATE FUNCTION public.remove_follower(user_id uuid, follower_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
	BEGIN
		DELETE FROM followers WHERE user_id = user_id AND follower_id = follower_id;
		return true;
	END;
$$;
 F   DROP FUNCTION public.remove_follower(user_id uuid, follower_id uuid);
       public          social_demo_admin    false            E           0    0 8   FUNCTION remove_follower(user_id uuid, follower_id uuid)    ACL     f   GRANT ALL ON FUNCTION public.remove_follower(user_id uuid, follower_id uuid) TO social_demo_api_role;
          public          social_demo_admin    false    248            �            1259    8233985 	   followers    TABLE     t   CREATE TABLE public.followers (
    user_id uuid NOT NULL,
    follower_id uuid NOT NULL,
    create_time bigint
);
    DROP TABLE public.followers;
       public         heap    social_demo_admin    false            �            1259    8233988    images    TABLE     �   CREATE TABLE public.images (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    format character varying NOT NULL,
    is_profile boolean DEFAULT false NOT NULL,
    create_time bigint
);
    DROP TABLE public.images;
       public         heap    social_demo_admin    false    2            F           0    0    TABLE images    ACL     =   GRANT SELECT ON TABLE public.images TO social_demo_api_role;
          public          social_demo_admin    false    206            �            1259    8233993    posts    TABLE     Q  CREATE TABLE public.posts (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    user_id uuid,
    image_id uuid,
    content character varying(2048),
    create_time bigint,
    edited boolean DEFAULT false NOT NULL,
    edit_time bigint,
    visibility public.visibility_type DEFAULT 'public'::public.visibility_type NOT NULL
);
    DROP TABLE public.posts;
       public         heap    social_demo_admin    false    2    718    718            G           0    0    TABLE posts    ACL     <   GRANT SELECT ON TABLE public.posts TO social_demo_api_role;
          public          social_demo_admin    false    207            �            1259    8234000 
   room_users    TABLE     �   CREATE TABLE public.room_users (
    room_id uuid NOT NULL,
    user_id uuid NOT NULL,
    is_admin boolean NOT NULL,
    create_time bigint
);
    DROP TABLE public.room_users;
       public         heap 
   alex_mezga    false            �            1259    8234003    rooms    TABLE     �   CREATE TABLE public.rooms (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    owner_id uuid NOT NULL,
    image_id uuid,
    title character varying(2048),
    about character varying(1024),
    create_time bigint
);
    DROP TABLE public.rooms;
       public         heap    social_demo_admin    false    2            H           0    0    TABLE rooms    ACL     <   GRANT SELECT ON TABLE public.rooms TO social_demo_api_role;
          public          social_demo_admin    false    209            �            1259    8234010    users    TABLE     x  CREATE TABLE public.users (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    email character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    password_hash character varying NOT NULL,
    username text,
    create_time bigint,
    disabled boolean DEFAULT true NOT NULL,
    description character varying
);
    DROP TABLE public.users;
       public         heap    social_demo_admin    false    2            I           0    0    TABLE users    ACL     <   GRANT SELECT ON TABLE public.users TO social_demo_api_role;
          public          social_demo_admin    false    210            ,          0    8233985 	   followers 
   TABLE DATA           F   COPY public.followers (user_id, follower_id, create_time) FROM stdin;
    public          social_demo_admin    false    205   �[       -          0    8233988    images 
   TABLE DATA           N   COPY public.images (id, user_id, format, is_profile, create_time) FROM stdin;
    public          social_demo_admin    false    206   �\       .          0    8233993    posts 
   TABLE DATA           k   COPY public.posts (id, user_id, image_id, content, create_time, edited, edit_time, visibility) FROM stdin;
    public          social_demo_admin    false    207   S]       /          0    8234000 
   room_users 
   TABLE DATA           M   COPY public.room_users (room_id, user_id, is_admin, create_time) FROM stdin;
    public       
   alex_mezga    false    208   �a       0          0    8234003    rooms 
   TABLE DATA           R   COPY public.rooms (id, owner_id, image_id, title, about, create_time) FROM stdin;
    public          social_demo_admin    false    209   �a       1          0    8234010    users 
   TABLE DATA           ~   COPY public.users (id, email, first_name, last_name, password_hash, username, create_time, disabled, description) FROM stdin;
    public          social_demo_admin    false    210   �a       �           2606    8234018    followers followers_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.followers
    ADD CONSTRAINT followers_pkey PRIMARY KEY (user_id, follower_id);
 B   ALTER TABLE ONLY public.followers DROP CONSTRAINT followers_pkey;
       public            social_demo_admin    false    205    205            �           2606    8234020    images images_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.images DROP CONSTRAINT images_pkey;
       public            social_demo_admin    false    206            �           2606    8234022    posts posts_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_pkey;
       public            social_demo_admin    false    207            �           2606    8234024    rooms rooms_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.rooms DROP CONSTRAINT rooms_pkey;
       public            social_demo_admin    false    209            �           2606    8234026    rooms rooms_title_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_title_key UNIQUE (title);
 ?   ALTER TABLE ONLY public.rooms DROP CONSTRAINT rooms_title_key;
       public            social_demo_admin    false    209            �           2606    8234028    room_users unique_room_user 
   CONSTRAINT     b   ALTER TABLE ONLY public.room_users
    ADD CONSTRAINT unique_room_user UNIQUE (room_id, user_id);
 E   ALTER TABLE ONLY public.room_users DROP CONSTRAINT unique_room_user;
       public         
   alex_mezga    false    208    208            �           2606    8234030    users users_email_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);
 ?   ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
       public            social_demo_admin    false    210            �           2606    8234032    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            social_demo_admin    false    210            �           2606    8234033 $   followers followers_follower_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.followers
    ADD CONSTRAINT followers_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES public.users(id);
 N   ALTER TABLE ONLY public.followers DROP CONSTRAINT followers_follower_id_fkey;
       public          social_demo_admin    false    205    210    3233            �           2606    8234038     followers followers_user_id_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.followers
    ADD CONSTRAINT followers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 J   ALTER TABLE ONLY public.followers DROP CONSTRAINT followers_user_id_fkey;
       public          social_demo_admin    false    210    205    3233            �           2606    8234043    posts posts_image_id_fkey    FK CONSTRAINT     z   ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id);
 C   ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_image_id_fkey;
       public          social_demo_admin    false    3221    206    207            �           2606    8234048    posts posts_user_id_fkey    FK CONSTRAINT     w   ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 B   ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_user_id_fkey;
       public          social_demo_admin    false    3233    207    210            �           2606    8234053 "   room_users room_users_room_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.room_users
    ADD CONSTRAINT room_users_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);
 L   ALTER TABLE ONLY public.room_users DROP CONSTRAINT room_users_room_id_fkey;
       public       
   alex_mezga    false    3227    209    208            �           2606    8234058 "   room_users room_users_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.room_users
    ADD CONSTRAINT room_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 L   ALTER TABLE ONLY public.room_users DROP CONSTRAINT room_users_user_id_fkey;
       public       
   alex_mezga    false    3233    208    210            �           2606    8234063    rooms rooms_image_id_fkey    FK CONSTRAINT     z   ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id);
 C   ALTER TABLE ONLY public.rooms DROP CONSTRAINT rooms_image_id_fkey;
       public          social_demo_admin    false    3221    206    209            �           2606    8234068    rooms rooms_owner_id_fkey    FK CONSTRAINT     y   ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);
 C   ALTER TABLE ONLY public.rooms DROP CONSTRAINT rooms_owner_id_fkey;
       public          social_demo_admin    false    3233    209    210            ,   �   x���;�1�:�㽼c{�K�Dz�g���JQE�̞�;&�쀅K�s��2�+��E�gw�X��.����E��>��,�����C0��
���!�Mq2����m]I���Xz����(MӮ���㠜I� ��I���)�ֽ�)��v���)��Ƹ�搵Hƅ.0:m�9ٔ���¨��[k�>��      -   �   x��ͻ�0 �Zڅ	��vICɔ� ������s�0��@uO�,Y�B�/Fk�]Us��ׄ��IO2.�o�����,��3����ሲ�>;_�0��@�{���A�k.��8ag(i@w�A�&
�qG��G��f^L�      .   )  x���K�$G��ݧ �����#`6a�4/M����MΫ3�^T��M��R�%��O�Q��VJ�g��΀�ѐY�wJ �	d����p�<I�ݛ�w��_�>~x|��r�,�6�[�/?��~�);#h7IX�fX�tXS/&w�#�Y*mnjB��ܫ�^��~��0ߏ=P�f�
\_~|��"+'��o���F�)KJR�_�3�"i��M(j�ƂFư�VU��|��;f;2q��	��VY�S�<��j��S�Ĕgf9�6Z6�X��
R]��mh��k�v��;橶^��f�Q@F��Ph�B��(x3��/�<)��A������ؒ͔��\���t,��	��qJ$��9�$�9,��1k\r�z)ǝ~�c������-�5�^GH��Ӻ�|�OKx@ΐ��K�B�Z7�}_2�e�;d:Vנ���	�Ӡ��v�cМ�#?=�iO�%�o�����{{{�Fe$Q(�!s�`�X�Z�:y���w�˙ڦ��(6�xDm�䨱�0�!ɬ�������D]2�����&��	�[�S�R���tO�Ɉ�vIJ:�cf$6��3S�h2���W���Q�5fQF��R�,�����wV�0��T�Q�Nʹ�����%E����h�)C�f����W�U��o�\��'K��Z)f(%����m^/s��䳒)�J�4+1�aڡ)����k���_'�3��;l-���B��Xjm#F*K.�� ������nr�8�V�ң�<h�\�������]��J�ʑ[�S��b?��z�޽B�2���b��~
��?D��x�7����ˉ���k�Xst#izQ�w^����׭řf�CH.�X��n�l#��s+a	�*5��GkG*!+��#E�m;K�۱�S��:�RyG-G��99�K9��G��<����V�#�F��=e�f���Dղ0P��#ci��\����٤�^	R&_��ͩ� ��U�}�I���g��+��q�!o(�@��V�S��f���/,��e��>�ͦ��FDi`��9�ss���-n�·��M�t ��������      /      x������ � �      0      x������ � �      1   D  x���Ko�@�3|�r]��ǭ��#�@ �zY�1`�`0��J�T$.si~��C�f �� @C'@ M \ ��;�p-q�J{�cn���U�ױgҤ֌]�w�e�ת!ҵ'<!�T�0o�#��S���mG�h4j�;s������i�f?�i9l����)5�1�TB�j�Z���1��:��v��ι�N�D�H	-tŖ��I`�%kk��7b� ��}�-�m�x�^�+]m_z�0[���Q�iN'y/����}%�o3����R%��)F 14������6e�y��	"��FÂM��^�/ph��eA��a���K����ô5�o��w�Z� � U�-R@	� �(V<���L0G�)�,�/��}u��n�٨7�������d�!;��R�j��	|[_���Y�1S`(�˰
���6���j��#�3{���٩�)j���7y���q?�z��<G�h���N������ٷY�{fͪ&�6�b�Fa0�*@�r.o��s|�2�)Ud��o��V�3W�-8�'g�|z�A.��.�ˢh}v���̯f%������W���S<     