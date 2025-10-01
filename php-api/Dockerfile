FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y unzip git \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

WORKDIR /var/www/html

COPY composer.json composer.lock* ./
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
    && php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
    && php -r "unlink('composer-setup.php');" \
    && composer install --no-dev --no-interaction --prefer-dist \
    && rm -rf /root/.composer

COPY public/ /var/www/html/

RUN sed -i 's#DocumentRoot /var/www/html#DocumentRoot /var/www/html/public#' /etc/apache2/sites-available/000-default.conf \
    && sed -i 's#<Directory /var/www/>#<Directory /var/www/html/public/>#' /etc/apache2/apache2.conf \
    && echo "<Directory /var/www/html/public/>\n    AllowOverride All\n    Require all granted\n</Directory>" > /etc/apache2/conf-available/api-override.conf \
    && a2enconf api-override

EXPOSE 80
CMD ["apache2-foreground"]
