/* eslint-disable */
const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: {
        main: './decruck/static/src/main.js',
    },
    mode: process.env.WEBPACK_SERVE ? 'development' : 'production',
    output: {
        path: path.resolve(__dirname, 'decruck/static/build'),
        filename: 'bundle.js'
    },
    resolve: {
        extensions: ['*', '.js']
    },
    module: {
        rules: [
            {
                test: /\.(js)$/,
                include: path.resolve(__dirname, 'decruck/static/src'),
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            },
            {
                test: /\.(scss)$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            sourceMap: true,
                        }
                    },
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: true,
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            plugins: function() {
                                return [
                                    require('precss'),
                                    require('autoprefixer')
                                ]
                            },
                            sourceMap: true,
                        }
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: true,
                        }
                    }
                ]
            },
        ],
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name].css',
            chunkFilename: '[id].css',
        }),
    ]
};
