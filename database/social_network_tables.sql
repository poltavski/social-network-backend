create table images
(
    id          uuid    default public.gen_random_uuid() not null
        constraint images_pkey
            primary key,
    user_id     uuid                                     not null,
    format      varchar                                  not null,
    is_profile  boolean default false                    not null,
    create_time bigint
);

alter table images
    owner to social_demo_admin;

grant select on images to social_demo_api_role;

create table users
(
    id            uuid    default public.gen_random_uuid() not null
        constraint users_pkey
            primary key,
    email         varchar                                  not null
        constraint users_email_key
            unique,
    first_name    varchar                                  not null,
    last_name     varchar                                  not null,
    password_hash varchar                                  not null,
    username      text,
    create_time   bigint,
    disabled      boolean default true                     not null,
    description   varchar
);

alter table users
    owner to social_demo_admin;

create table followers
(
    user_id     uuid not null
        constraint followers_user_id_fkey
            references users,
    follower_id uuid not null
        constraint followers_follower_id_fkey
            references users,
    create_time bigint,
    constraint followers_pkey
        primary key (user_id, follower_id)
);

alter table followers
    owner to social_demo_admin;

create table posts
(
    id          uuid            default public.gen_random_uuid()  not null
        constraint posts_pkey
            primary key,
    user_id     uuid
        constraint posts_user_id_fkey
            references users,
    image_id    uuid
        constraint posts_image_id_fkey
            references images,
    content     varchar(2048),
    create_time bigint,
    edited      boolean         default false                     not null,
    edit_time   bigint,
    visibility  visibility_type default 'public'::visibility_type not null,
    likes       character varying[]
);

alter table posts
    owner to social_demo_admin;

grant select on posts to social_demo_api_role;

create table rooms
(
    id          uuid default public.gen_random_uuid() not null
        constraint rooms_pkey
            primary key,
    owner_id    uuid                                  not null
        constraint rooms_owner_id_fkey
            references users,
    image_id    uuid
        constraint rooms_image_id_fkey
            references images,
    title       varchar(2048)
        constraint rooms_title_key
            unique,
    about       varchar(1024),
    create_time bigint
);

alter table rooms
    owner to social_demo_admin;

create table room_users
(
    room_id     uuid    not null
        constraint room_users_room_id_fkey
            references rooms,
    user_id     uuid    not null
        constraint room_users_user_id_fkey
            references users,
    is_admin    boolean not null,
    create_time bigint,
    constraint unique_room_user
        unique (room_id, user_id)
);

alter table room_users
    owner to alex_mezga;

grant select on rooms to social_demo_api_role;

grant select on users to social_demo_api_role;


