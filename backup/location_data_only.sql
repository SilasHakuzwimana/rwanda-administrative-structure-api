CREATE TABLE `countries` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `countries`
--

INSERT INTO `countries` (`id`, `name`) VALUES
(1, 'Rwanda');

-- --------------------------------------------------------

--
-- Table structure for table `districts`
--

CREATE TABLE `districts` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `province_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `districts`
--

INSERT INTO `districts` (`id`, `name`, `province_id`) VALUES
(30, 'Bugesera', 5),
(22, 'Burera', 4),
(20, 'Gakenke', 4),
(2, 'Gasabo', 1),
(26, 'Gatsibo', 5),
(23, 'Gicumbi', 4),
(5, 'Gisagara', 2),
(7, 'Huye', 2),
(11, 'Kamonyi', 2),
(12, 'Karongi', 3),
(27, 'Kayonza', 5),
(3, 'Kicukiro', 1),
(28, 'Kirehe', 5),
(10, 'Muhanga', 2),
(21, 'Musanze', 4),
(29, 'Ngoma', 5),
(16, 'Ngororero', 3),
(15, 'Nyabihu', 3),
(25, 'Nyagatare', 5),
(8, 'Nyamagabe', 2),
(18, 'Nyamasheke', 3),
(4, 'Nyanza', 2),
(1, 'Nyarugenge', 1),
(6, 'Nyaruguru', 2),
(14, 'Rubavu', 3),
(9, 'Ruhango', 2),
(19, 'Rulindo', 4),
(17, 'Rusizi', 3),
(13, 'Rutsiro', 3),
(24, 'Rwamagana', 5);

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL
) ;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-05-16 10:25:55.996582', '1', 'Kigali City', 1, '[{\"added\": {}}]', 8, 1),
(2, '2025-05-16 10:26:34.636011', '2', 'Southern Province', 1, '[{\"added\": {}}]', 8, 1),
(3, '2025-05-16 10:26:51.090117', '3', 'Western Province', 1, '[{\"added\": {}}]', 8, 1),
(4, '2025-05-16 10:27:06.394654', '4', 'Northern Province', 1, '[{\"added\": {}}]', 8, 1),
(5, '2025-05-16 10:27:22.012913', '5', 'Eastern Province', 1, '[{\"added\": {}}]', 8, 1),
(6, '2025-05-16 10:28:41.381856', '1', 'Nyarugenge', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(7, '2025-05-16 10:30:13.146093', '2', 'Gasabo', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(8, '2025-05-16 10:30:59.858220', '5', 'Eastern Province', 2, '[]', 8, 1),
(9, '2025-05-16 10:31:07.292501', '1', 'Kigali City', 2, '[]', 8, 1),
(10, '2025-05-16 11:02:13.770510', '5', 'Gisagara', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(11, '2025-05-16 11:02:13.774042', '7', 'Huye', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(12, '2025-05-16 11:02:13.774730', '11', 'Kamonyi', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(13, '2025-05-16 11:02:13.774730', '12', 'Karongi', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(14, '2025-05-16 11:02:13.781965', '3', 'Kicukiro', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(15, '2025-05-16 11:02:13.787681', '10', 'Muhanga', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(16, '2025-05-16 11:02:13.792751', '8', 'Nyamagabe', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(17, '2025-05-16 11:02:13.792751', '4', 'Nyanza', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(18, '2025-05-16 11:02:13.799913', '6', 'Nyaruguru', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(19, '2025-05-16 11:02:13.802939', '14', 'Rubavu', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(20, '2025-05-16 11:02:22.614069', '9', 'Ruhango', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(21, '2025-05-16 11:02:22.619063', '13', 'Rutsiro', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(22, '2025-05-16 11:13:24.674731', '16', 'Ngororero', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(23, '2025-05-16 11:13:24.674731', '15', 'Nyabihu', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(24, '2025-05-16 11:13:24.674731', '18', 'Nyamasheke', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(25, '2025-05-16 11:13:24.684211', '17', 'Rusizi', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(26, '2025-05-16 11:39:32.446695', '22', 'Burera', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(27, '2025-05-16 11:39:32.456822', '20', 'Gakenke', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(28, '2025-05-16 11:39:32.456822', '23', 'Gicumbi', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(29, '2025-05-16 11:39:32.456822', '21', 'Musanze', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1),
(30, '2025-05-16 11:39:32.463692', '19', 'Rulindo', 2, '[{\"changed\": {\"fields\": [\"Province\"]}}]', 9, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(13, 'authtoken', 'token'),
(14, 'authtoken', 'tokenproxy'),
(5, 'contenttypes', 'contenttype'),
(11, 'location', 'cell'),
(7, 'location', 'country'),
(9, 'location', 'district'),
(8, 'location', 'province'),
(10, 'location', 'sector'),
(12, 'location', 'village'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-05-16 10:21:06.912313'),
(2, 'auth', '0001_initial', '2025-05-16 10:21:08.687189'),
(3, 'admin', '0001_initial', '2025-05-16 10:21:08.921649'),
(4, 'admin', '0002_logentry_remove_auto_add', '2025-05-16 10:21:08.932037'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-05-16 10:21:08.946467'),
(6, 'contenttypes', '0002_remove_content_type_name', '2025-05-16 10:21:09.130916'),
(7, 'auth', '0002_alter_permission_name_max_length', '2025-05-16 10:21:09.225868'),
(8, 'auth', '0003_alter_user_email_max_length', '2025-05-16 10:21:09.284658'),
(9, 'auth', '0004_alter_user_username_opts', '2025-05-16 10:21:09.298620'),
(10, 'auth', '0005_alter_user_last_login_null', '2025-05-16 10:21:09.416281'),
(11, 'auth', '0006_require_contenttypes_0002', '2025-05-16 10:21:09.422246'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2025-05-16 10:21:09.433758'),
(13, 'auth', '0008_alter_user_username_max_length', '2025-05-16 10:21:09.502658'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2025-05-16 10:21:09.601516'),
(15, 'auth', '0010_alter_group_name_max_length', '2025-05-16 10:21:09.664804'),
(16, 'auth', '0011_update_proxy_permissions', '2025-05-16 10:21:09.688537'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2025-05-16 10:21:09.749000'),
(18, 'authtoken', '0001_initial', '2025-05-16 10:21:09.904006'),
(19, 'authtoken', '0002_auto_20160226_1747', '2025-05-16 10:21:09.930608'),
(20, 'authtoken', '0003_tokenproxy', '2025-05-16 10:21:09.942048'),
(21, 'authtoken', '0004_alter_tokenproxy_options', '2025-05-16 10:21:09.948088'),
(22, 'location', '0001_initial', '2025-05-16 10:21:10.538860'),
(23, 'location', '0002_alter_cell_options_alter_district_options_and_more', '2025-05-16 10:21:11.106397'),
(24, 'sessions', '0001_initial', '2025-05-16 10:21:11.213433');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('jna2zemlwlrctk0qekudvke2o818ruxl', '.eJxVjEEOwiAQRe_C2hCg4FCX7nsGMjCMVA0kpV0Z765NutDtf-_9lwi4rSVsPS9hJnERWpx-t4jpkesO6I711mRqdV3mKHdFHrTLqVF-Xg_376BgL98aBqLBRIazSj5lFS1bZoWOfAIgrw0BKQbDigxpVt7bjDSaUTtwmMX7A_3cOGk:1uFsFv:GJtFAbF9FZ7AOwWva_C6XStRVPawQUSSHA0eFO6rvBo', '2025-05-30 10:25:31.810978');

-- --------------------------------------------------------

--
-- Table structure for table `provinces`
--

CREATE TABLE `provinces` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `country_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `provinces`
--

INSERT INTO `provinces` (`id`, `name`, `country_id`) VALUES
(5, 'Eastern Province', 1),
(1, 'Kigali City', 1),
(4, 'Northern Province', 1),
(2, 'Southern Province', 1),
(3, 'Western Province', 1);

-- --------------------------------------------------------

--
-- Table structure for table `sectors`
--

CREATE TABLE `sectors` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `district_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sectors`
--

INSERT INTO `sectors` (`id`, `name`, `district_id`) VALUES
(233, 'BASE', 19),
(175, 'Bigogwe', 15),
(150, 'Boneza', 13),
(200, 'Bugarama', 17),
(163, 'Bugeshi', 14),
(301, 'Bukure', 23),
(11, 'Bumbogo', 2),
(284, 'Bungwe', 22),
(234, 'BUREGA', 19),
(87, 'Buruhukiro', 8),
(59, 'Busanze', 6),
(36, 'Busasamana', 4),
(164, 'Busasamana', 14),
(250, 'Busengo', 20),
(218, 'Bushekeri', 18),
(219, 'Bushenge', 18),
(235, 'BUSHOKI', 19),
(269, 'Busogo', 21),
(37, 'Busoro', 4),
(201, 'Butare', 17),
(285, 'Butaro', 22),
(236, 'BUYOGA', 19),
(104, 'Bweramana', 9),
(202, 'Bweyeye', 17),
(187, 'BWIRA', 16),
(137, 'Bwishyura', 12),
(302, 'Bwisige', 23),
(105, 'Byimana', 9),
(303, 'Byumba', 23),
(251, 'Coko', 20),
(38, 'Cyabakamyi', 4),
(252, 'Cyabingo', 20),
(60, 'Cyahinda', 6),
(88, 'Cyanika', 8),
(286, 'Cyanika', 22),
(165, 'Cyanzarwe', 14),
(220, 'Cyato', 18),
(287, 'Cyeru', 22),
(113, 'Cyeza', 10),
(237, 'CYINZUZI', 19),
(304, 'Cyumba', 23),
(238, 'CYUNGO', 19),
(270, 'Cyuve', 21),
(322, 'Fumbwe', 24),
(271, 'Gacaca', 21),
(125, 'Gacurabwenge', 11),
(26, 'Gahanga', 3),
(376, 'Gahara', 28),
(323, 'Gahengeri', 24),
(364, 'Gahini', 27),
(288, 'Gahunga', 22),
(253, 'Gakenke', 20),
(89, 'Gasaka', 8),
(350, 'Gasange', 26),
(272, 'Gashaki', 21),
(388, 'Gashanda', 29),
(138, 'Gashari', 12),
(254, 'Gashenyi', 20),
(203, 'Gashonga', 17),
(402, 'Gashora', 30),
(273, 'Gataraga', 21),
(90, 'Gatare', 8),
(289, 'Gatebe', 22),
(27, 'Gatenga', 3),
(377, 'Gatore', 28),
(12, 'Gatsata', 2),
(351, 'Gatsibo', 26),
(188, 'GATUMBA', 16),
(336, 'GATUNDA', 25),
(151, 'Gihango', 13),
(204, 'Giheke', 17),
(221, 'Gihombo', 18),
(205, 'Gihundwe', 17),
(13, 'Gikomero', 2),
(28, 'Gikondo', 3),
(46, 'Gikonko', 5),
(206, 'Gikundamvura', 17),
(166, 'Gisenyi', 14),
(324, 'Gishali', 24),
(73, 'Gishamvu', 7),
(47, 'Gishubi', 5),
(139, 'Gishyita', 12),
(14, 'Gisozi', 2),
(207, 'Gitambi', 17),
(1, 'Gitega', 1),
(140, 'Gitesi', 12),
(305, 'Giti', 23),
(352, 'Gitoki', 26),
(290, 'Gitovu', 22),
(189, 'HINDIRO', 16),
(74, 'Huye', 7),
(15, 'Jabana', 2),
(16, 'Jali', 2),
(255, 'Janja', 20),
(389, 'Jarama', 29),
(176, 'Jenda', 15),
(177, 'Jomba', 15),
(403, 'Juru', 30),
(114, 'Kabacuzi', 10),
(106, 'Kabagali', 9),
(365, 'Kabare', 27),
(366, 'Kabarondo', 27),
(353, 'Kabarore', 26),
(178, 'Kabatwa', 15),
(190, 'KABAYA', 16),
(17, 'Kacyiru', 2),
(91, 'Kaduha', 8),
(222, 'Kagano', 18),
(29, 'Kagarama', 3),
(191, 'KAGEYO', 16),
(306, 'Kageyo', 23),
(354, 'Kageyo', 26),
(291, 'Kagogo', 22),
(404, 'Kamabuye', 30),
(92, 'Kamegeri', 8),
(208, 'Kamembe', 17),
(256, 'Kamubuga', 20),
(167, 'Kanama', 14),
(307, 'Kaniga', 23),
(223, 'Kanjongo', 18),
(30, 'Kanombe', 3),
(48, 'Kansi', 5),
(2, 'Kanyinya', 1),
(168, 'Kanzenze', 14),
(179, 'Karago', 15),
(75, 'Karama', 7),
(126, 'Karama', 11),
(337, 'KARAMA', 25),
(224, 'Karambi', 18),
(257, 'Karambo', 20),
(338, 'KARANGAZI', 25),
(390, 'Karembo', 29),
(325, 'Karenge', 24),
(225, 'Karengera', 18),
(339, 'KATABAGEMU', 25),
(192, 'KAVUMU', 16),
(127, 'Kayenzi', 11),
(128, 'Kayumbu', 11),
(391, 'Kazo', 29),
(115, 'Kibangu', 10),
(61, 'Kibeho', 6),
(39, 'Kibilizi', 4),
(49, 'Kibirizi', 5),
(93, 'Kibirizi', 8),
(94, 'Kibumbwe', 8),
(392, 'Kibungo', 29),
(31, 'Kicukiro', 3),
(326, 'Kigabiro', 24),
(3, 'Kigali', 1),
(32, 'Kigarama', 3),
(378, 'Kigarama', 28),
(50, 'Kigembe', 5),
(152, 'Kigeyo', 13),
(379, 'Kigina', 28),
(40, 'Kigoma', 4),
(76, 'Kigoma', 7),
(18, 'Kimihurura', 2),
(19, 'Kimironko', 2),
(4, 'Kimisagara', 1),
(274, 'Kimonyi', 21),
(77, 'Kinazi', 7),
(107, 'Kinazi', 9),
(275, 'Kinigi', 21),
(108, 'Kinihira', 9),
(239, 'KINIHIRA', 19),
(292, 'Kinoni', 22),
(180, 'Kintobo', 15),
(293, 'Kinyababa', 22),
(20, 'Kinyinya', 2),
(355, 'Kiramuruzi', 26),
(380, 'Kirehe', 28),
(226, 'Kirimbi', 18),
(240, 'KISARO', 19),
(95, 'Kitabi', 8),
(62, 'Kivu', 6),
(153, 'Kivumu', 13),
(258, 'Kivuruga', 20),
(294, 'Kivuye', 22),
(340, 'KIYOMBE', 25),
(116, 'Kiyumba', 10),
(356, 'Kiziguro', 26),
(227, 'Macuba', 18),
(5, 'Mageragere', 1),
(381, 'Mahama', 28),
(228, 'Mahembe', 18),
(51, 'Mamba', 5),
(154, 'Manihira', 13),
(308, 'Manyagiro', 23),
(78, 'Maraba', 7),
(405, 'Mareba', 30),
(33, 'Masaka', 3),
(241, 'MASORO', 19),
(63, 'Mata', 6),
(259, 'Mataba', 20),
(341, 'MATIMBA', 25),
(193, 'MATYAZO', 16),
(406, 'Mayange', 30),
(79, 'Mbazi', 7),
(96, 'Mbazi', 8),
(242, 'MBOGO', 19),
(109, 'Mbuye', 9),
(342, 'MIMURI', 25),
(260, 'Minazi', 20),
(309, 'Miyove', 23),
(382, 'Mpanga', 28),
(141, 'Mubuga', 12),
(169, 'Mudende', 14),
(97, 'Mugano', 8),
(52, 'Muganza', 5),
(64, 'Muganza', 6),
(209, 'Muganza', 17),
(393, 'Mugesera', 29),
(129, 'Mugina', 11),
(53, 'Mugombwa', 5),
(261, 'Mugunga', 20),
(194, 'MUHANDA', 16),
(117, 'Muhanga', 10),
(327, 'Muhazi', 24),
(6, 'Muhima', 1),
(262, 'Muhondo', 20),
(195, 'MUHORORO', 16),
(276, 'Muhoza', 21),
(357, 'Muhura', 26),
(343, 'MUKAMA', 25),
(181, 'Mukamira', 15),
(310, 'Mukarange', 23),
(367, 'Mukarange', 27),
(54, 'Mukindo', 5),
(41, 'Mukingo', 4),
(277, 'Muko', 21),
(311, 'Muko', 23),
(80, 'Mukura', 7),
(155, 'Mukura', 13),
(65, 'Munini', 6),
(328, 'Munyaga', 24),
(329, 'Munyiginya', 24),
(368, 'Murama', 27),
(394, 'Murama', 29),
(142, 'Murambi', 12),
(243, 'MURAMBI', 19),
(358, 'Murambi', 26),
(182, 'Muringa', 15),
(156, 'Murunda', 13),
(143, 'Murundi', 12),
(369, 'Murundi', 27),
(210, 'Mururu', 17),
(130, 'Musambira', 11),
(98, 'Musange', 8),
(278, 'Musanze', 21),
(157, 'Musasa', 13),
(383, 'Musaza', 28),
(99, 'Musebeya', 8),
(407, 'Musenyi', 30),
(55, 'Musha', 5),
(330, 'Musha', 24),
(344, 'MUSHERI', 25),
(384, 'Mushikiri', 28),
(118, 'Mushishiro', 10),
(158, 'Mushonyi', 13),
(159, 'Mushubati', 13),
(100, 'Mushubi', 8),
(395, 'Mutenderi', 29),
(312, 'Mutete', 23),
(144, 'Mutuntu', 12),
(42, 'Muyira', 4),
(263, 'Muyongwe', 20),
(331, 'Muyumbu', 24),
(264, 'Muzo', 20),
(110, 'Mwendo', 9),
(370, 'Mwiri', 27),
(408, 'Mwogo', 30),
(332, 'Mwulire', 24),
(385, 'Nasho', 28),
(196, 'NDARO', 16),
(371, 'Ndego', 27),
(21, 'Ndera', 2),
(56, 'Ndora', 5),
(22, 'Nduba', 2),
(265, 'Nemba', 20),
(295, 'Nemba', 22),
(131, 'Ngamba', 11),
(359, 'Ngarama', 26),
(66, 'Ngera', 6),
(409, 'Ngeruka', 30),
(67, 'Ngoma', 6),
(81, 'Ngoma', 7),
(244, 'NGOMA', 19),
(197, 'NGORORERO', 16),
(34, 'Niboye', 3),
(211, 'Nkanka', 17),
(101, 'Nkomane', 8),
(212, 'Nkombo', 17),
(279, 'Nkotsi', 21),
(213, 'Nkungu', 17),
(245, 'NTARABANA', 19),
(410, 'Ntarama', 30),
(111, 'Ntongwe', 9),
(43, 'Ntyazo', 4),
(68, 'Nyabimata', 6),
(119, 'Nyabinoni', 10),
(160, 'Nyabirasi', 13),
(229, 'Nyabitekeri', 18),
(345, 'NYAGATARE', 25),
(360, 'Nyagihanga', 26),
(44, 'Nyagisozi', 4),
(69, 'Nyagisozi', 6),
(7, 'Nyakabanda', 1),
(214, 'Nyakabuye', 17),
(333, 'Nyakaliro', 24),
(215, 'Nyakarenzo', 17),
(170, 'Nyakiriba', 14),
(120, 'Nyamabuye', 10),
(411, 'Nyamata', 30),
(372, 'Nyamirama', 27),
(8, 'Nyamirambo', 1),
(132, 'Nyamiyaga', 11),
(313, 'Nyamiyaga', 23),
(386, 'Nyamugari', 28),
(171, 'Nyamyumba', 14),
(198, 'NYANGE', 16),
(280, 'Nyange', 21),
(314, 'Nyankenke', 23),
(57, 'Nyanza', 5),
(133, 'Nyarubaka', 11),
(387, 'Nyarubuye', 28),
(9, 'Nyarugenge', 1),
(412, 'Nyarugenge', 30),
(35, 'Nyarugunga', 3),
(121, 'Nyarusange', 10),
(172, 'Nyundo', 14),
(216, 'Nzahaha', 17),
(334, 'Nzige', 24),
(183, 'Rambura', 15),
(230, 'Rangiro', 18),
(23, 'Remera', 2),
(281, 'Remera', 21),
(361, 'Remera', 26),
(396, 'Remera', 29),
(413, 'Ririma', 30),
(122, 'Rongi', 10),
(173, 'Rubavu', 14),
(315, 'Rubaya', 23),
(145, 'Rubengera', 12),
(335, 'Rubona', 24),
(146, 'Rugabano', 12),
(147, 'Ruganda', 12),
(296, 'Rugarama', 22),
(362, 'Rugarama', 26),
(134, 'Rugarika', 11),
(123, 'Rugendabari', 10),
(297, 'Rugendabari', 22),
(184, 'Rugera', 15),
(174, 'Rugerero', 14),
(112, 'Ruhango', 9),
(161, 'Ruhango', 13),
(231, 'Ruharambuga', 18),
(82, 'Ruhashya', 7),
(70, 'Ruheru', 6),
(414, 'Ruhuha', 30),
(298, 'Ruhunde', 22),
(373, 'Rukara', 27),
(397, 'Rukira', 29),
(135, 'Rukoma', 11),
(316, 'Rukomo', 23),
(346, 'RUKOMO', 25),
(246, 'RUKOZO', 19),
(398, 'Rukumberi', 29),
(266, 'Ruli', 20),
(136, 'Runda', 11),
(71, 'Ruramba', 6),
(374, 'Ruramira', 27),
(185, 'Rurembo', 15),
(399, 'Rurenge', 29),
(299, 'Rusarabuye', 22),
(267, 'Rusasa', 20),
(83, 'Rusatira', 7),
(162, 'Rusebeya', 13),
(72, 'Rusenge', 6),
(317, 'Rushaki', 23),
(268, 'Rushashi', 20),
(247, 'RUSIGA', 19),
(24, 'Rusororo', 2),
(318, 'Rutare', 23),
(25, 'Rutunga', 2),
(319, 'Ruvune', 23),
(45, 'Rwabicuma', 4),
(320, 'Rwamiko', 23),
(84, 'Rwaniro', 7),
(148, 'Rwankuba', 12),
(282, 'Rwaza', 21),
(347, 'RWEMPASHA', 25),
(300, 'Rwerere', 22),
(415, 'Rweru', 30),
(10, 'Rwezamenyo', 1),
(217, 'Rwimbogo', 17),
(363, 'Rwimbogo', 26),
(348, 'RWIMIYAGA', 25),
(375, 'Rwinkwavu', 27),
(400, 'Sake', 29),
(58, 'Save', 5),
(321, 'Shangasha', 23),
(232, 'Shangi', 18),
(283, 'Shingiro', 21),
(416, 'Shyara', 30),
(186, 'Shyira', 15),
(124, 'Shyogwe', 10),
(248, 'SHYORONGI', 19),
(85, 'Simbi', 7),
(199, 'SOVU', 16),
(349, 'TABAGWE', 25),
(102, 'Tare', 8),
(86, 'Tumba', 7),
(249, 'TUMBA', 19),
(149, 'Twumba', 12),
(103, 'Uwinkingi', 8),
(401, 'Zaza', 29);

-- --------------------------------------------------------

--
-- Table structure for table `villages`
--

CREATE TABLE `villages` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `cell_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `villages`
--

INSERT INTO `villages` (`id`, `name`, `cell_id`) VALUES
