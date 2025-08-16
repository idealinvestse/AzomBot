<?php
/**
 * Plugin Name: AZOM Bot Embed
 * Description: Embed the AZOM AI Agent chatbot on your WordPress site with configurable settings.
 * Version: 0.1.0
 * Author: AZOM / IdealInvest
 * License: MIT
 * License URI: https://opensource.org/licenses/MIT
 * Text Domain: azom-bot
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly.
}

class AZOM_Bot_Plugin {
    const OPTION_KEY = 'azom_bot_options';
    const VERSION = '0.1.0';

    private static $instance = null;

    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        // Activation hook - set defaults
        register_activation_hook(__FILE__, [$this, 'activate']);

        // Admin settings
        add_action('admin_menu', [$this, 'add_admin_menu']);
        add_action('admin_init', [$this, 'register_settings']);

        // Frontend assets + shortcode
        add_action('wp_enqueue_scripts', [$this, 'register_assets']);
        add_shortcode('azom_bot', [$this, 'shortcode_render']);
    }

    public function activate() {
        $defaults = [
            'base_url'      => 'http://localhost:8001',
            'api_type'      => 'pipeline', // pipeline | core
            'endpoint_path' => '/chat/azom', // pipeline default
            'default_mode'  => 'light', // light | full
            'title'         => 'AZOM Support',
            'welcome'       => 'Hej! Hur kan jag hjälpa dig idag?',
            'position'      => 'right', // right | left
            'color'         => '#2563eb',
            'button_label'  => 'Chatta med AZOM',
            'show_everywhere' => 0,
        ];
        $current = get_option(self::OPTION_KEY);
        if (!is_array($current)) {
            update_option(self::OPTION_KEY, $defaults);
        } else {
            update_option(self::OPTION_KEY, array_merge($defaults, $current));
        }
    }

    public function add_admin_menu() {
        add_options_page(
            __('AZOM Bot', 'azom-bot'),
            __('AZOM Bot', 'azom-bot'),
            'manage_options',
            'azom-bot',
            [$this, 'render_settings_page']
        );
    }

    public function register_settings() {
        register_setting(self::OPTION_KEY, self::OPTION_KEY, [
            'type' => 'array',
            'sanitize_callback' => [$this, 'sanitize_options'],
            'default' => [],
        ]);

        add_settings_section(
            'azom_bot_main',
            __('AZOM Bot Settings', 'azom-bot'),
            function () {
                echo '<p>' . esc_html__('Configure how the AZOM chatbot connects to your backend and appears to users.', 'azom-bot') . '</p>';
            },
            self::OPTION_KEY
        );

        $fields = [
            'base_url' => __('Backend Base URL', 'azom-bot'),
            'api_type' => __('API Type', 'azom-bot'),
            'endpoint_path' => __('Endpoint Path', 'azom-bot'),
            'default_mode' => __('Default Mode', 'azom-bot'),
            'title' => __('Widget Title', 'azom-bot'),
            'welcome' => __('Welcome Message', 'azom-bot'),
            'position' => __('Position', 'azom-bot'),
            'color' => __('Primary Color', 'azom-bot'),
            'button_label' => __('Button Label', 'azom-bot'),
            'show_everywhere' => __('Show on all pages', 'azom-bot'),
        ];

        foreach ($fields as $key => $label) {
            add_settings_field(
                $key,
                $label,
                [$this, 'render_field_' . $key],
                self::OPTION_KEY,
                'azom_bot_main',
                ['key' => $key]
            );
        }
    }

    public function sanitize_options($input) {
        $output = [];
        $output['base_url'] = isset($input['base_url']) ? esc_url_raw($input['base_url']) : '';
        $output['api_type'] = (isset($input['api_type']) && in_array($input['api_type'], ['pipeline','core'], true)) ? $input['api_type'] : 'pipeline';
        $output['endpoint_path'] = isset($input['endpoint_path']) ? '/' . ltrim(sanitize_text_field($input['endpoint_path']), '/') : '/chat/azom';
        $output['default_mode'] = (isset($input['default_mode']) && in_array($input['default_mode'], ['light','full'], true)) ? $input['default_mode'] : 'light';
        $output['title'] = isset($input['title']) ? sanitize_text_field($input['title']) : '';
        $output['welcome'] = isset($input['welcome']) ? sanitize_text_field($input['welcome']) : '';
        $output['position'] = (isset($input['position']) && in_array($input['position'], ['left','right'], true)) ? $input['position'] : 'right';
        $output['color'] = isset($input['color']) ? sanitize_hex_color($input['color']) : '#2563eb';
        $output['button_label'] = isset($input['button_label']) ? sanitize_text_field($input['button_label']) : '';
        $output['show_everywhere'] = !empty($input['show_everywhere']) ? 1 : 0;
        return $output;
    }

    private function get_options() {
        $opts = get_option(self::OPTION_KEY, []);
        if (!is_array($opts)) { $opts = []; }
        return wp_parse_args($opts, [
            'base_url'      => 'http://localhost:8001',
            'api_type'      => 'pipeline',
            'endpoint_path' => '/chat/azom',
            'default_mode'  => 'light',
            'title'         => 'AZOM Support',
            'welcome'       => 'Hej! Hur kan jag hjälpa dig idag?',
            'position'      => 'right',
            'color'         => '#2563eb',
            'button_label'  => 'Chatta med AZOM',
            'show_everywhere' => 0,
        ]);
    }

    // Settings fields
    public function render_field_base_url($args) {
        $o = $this->get_options();
        printf('<input type="url" class="regular-text" name="%1$s[base_url]" value="%2$s" placeholder="http://localhost:8001" />', esc_attr(self::OPTION_KEY), esc_attr($o['base_url']));
        echo '<p class="description">' . esc_html__('Pipeline Server default is http://localhost:8001; Core API is typically http://localhost:8008', 'azom-bot') . '</p>';
    }
    public function render_field_api_type($args) {
        $o = $this->get_options();
        $val = $o['api_type'];
        echo '<select name="' . esc_attr(self::OPTION_KEY) . '[api_type]">';
        foreach (['pipeline' => 'Pipeline Server (/chat/azom)','core' => 'Core API (/api/v1/chat/azom)'] as $k => $label) {
            printf('<option value="%1$s" %2$s>%3$s</option>', esc_attr($k), selected($val, $k, false), esc_html($label));
        }
        echo '</select>';
    }
    public function render_field_endpoint_path($args) {
        $o = $this->get_options();
        printf('<input type="text" class="regular-text" name="%1$s[endpoint_path]" value="%2$s" />', esc_attr(self::OPTION_KEY), esc_attr($o['endpoint_path']));
        echo '<p class="description">' . esc_html__('E.g., /chat/azom for Pipeline Server; /api/v1/chat/azom for Core API.', 'azom-bot') . '</p>';
    }
    public function render_field_default_mode($args) {
        $o = $this->get_options();
        $val = $o['default_mode'];
        echo '<select name="' . esc_attr(self::OPTION_KEY) . '[default_mode]">';
        foreach (['light' => 'Light','full' => 'Full'] as $k => $label) {
            printf('<option value="%1$s" %2$s>%3$s</option>', esc_attr($k), selected($val, $k, false), esc_html($label));
        }
        echo '</select>';
        echo '<p class="description">' . esc_html__('Sends X-AZOM-Mode header with each request.', 'azom-bot') . '</p>';
    }
    public function render_field_title($args) {
        $o = $this->get_options();
        printf('<input type="text" class="regular-text" name="%1$s[title]" value="%2$s" />', esc_attr(self::OPTION_KEY), esc_attr($o['title']));
    }
    public function render_field_welcome($args) {
        $o = $this->get_options();
        printf('<input type="text" class="regular-text" name="%1$s[welcome]" value="%2$s" />', esc_attr(self::OPTION_KEY), esc_attr($o['welcome']));
    }
    public function render_field_position($args) {
        $o = $this->get_options();
        $val = $o['position'];
        echo '<select name="' . esc_attr(self::OPTION_KEY) . '[position]">';
        foreach (['right' => 'Bottom Right','left' => 'Bottom Left'] as $k => $label) {
            printf('<option value="%1$s" %2$s>%3$s</option>', esc_attr($k), selected($val, $k, false), esc_html($label));
        }
        echo '</select>';
    }
    public function render_field_color($args) {
        $o = $this->get_options();
        printf('<input type="text" class="regular-text" name="%1$s[color]" value="%2$s" class="azom-color" />', esc_attr(self::OPTION_KEY), esc_attr($o['color']));
    }
    public function render_field_button_label($args) {
        $o = $this->get_options();
        printf('<input type="text" class="regular-text" name="%1$s[button_label]" value="%2$s" />', esc_attr(self::OPTION_KEY), esc_attr($o['button_label']));
    }
    public function render_field_show_everywhere($args) {
        $o = $this->get_options();
        printf('<label><input type="checkbox" name="%1$s[show_everywhere]" value="1" %2$s /> %3$s</label>', esc_attr(self::OPTION_KEY), checked(1, $o['show_everywhere'], false), esc_html__('Always load widget on all pages (without shortcode)', 'azom-bot'));
    }

    public function render_settings_page() {
        if (!current_user_can('manage_options')) return;
        echo '<div class="wrap">';
        echo '<h1>' . esc_html__('AZOM Bot', 'azom-bot') . '</h1>';
        echo '<form method="post" action="options.php">';
        settings_fields(self::OPTION_KEY);
        do_settings_sections(self::OPTION_KEY);
        submit_button();
        echo '</form>';
        echo '<p class="description">' . esc_html__('Use the [azom_bot] shortcode to render the chat widget. Ensure CORS is enabled on your backend.', 'azom-bot') . '</p>';
        echo '</div>';
    }

    public function register_assets() {
        $suffix = defined('SCRIPT_DEBUG') && SCRIPT_DEBUG ? '' : '';
        wp_register_style('azom-bot-style', plugins_url('assets/css/widget.css', __FILE__), [], self::VERSION);
        wp_register_script('azom-bot-script', plugins_url('assets/js/widget.js', __FILE__), [], self::VERSION, true);

        // If show_everywhere, enqueue and localize
        $opts = $this->get_options();
        if (!is_admin() && !wp_doing_ajax() && !empty($opts['show_everywhere'])) {
            $this->enqueue_with_localized_settings();
        }
    }

    private function enqueue_with_localized_settings() {
        $opts = $this->get_options();
        wp_enqueue_style('azom-bot-style');
        wp_enqueue_script('azom-bot-script');
        wp_localize_script('azom-bot-script', 'AZOM_BOT_CONFIG', [
            'baseUrl' => esc_url_raw(rtrim($opts['base_url'], '/')),
            'apiType' => $opts['api_type'],
            'endpointPath' => '/' . ltrim($opts['endpoint_path'], '/'),
            'defaultMode' => $opts['default_mode'],
            'title' => $opts['title'],
            'welcome' => $opts['welcome'],
            'position' => $opts['position'],
            'color' => $opts['color'],
            'buttonLabel' => $opts['button_label'],
        ]);
    }

    public function shortcode_render($atts = [], $content = null) {
        $this->enqueue_with_localized_settings();
        // Container for the widget (JS will inject UI)
        return '<div id="azom-bot-root"></div>';
    }
}

AZOM_Bot_Plugin::instance();
