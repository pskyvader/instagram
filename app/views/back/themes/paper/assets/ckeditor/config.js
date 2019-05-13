/**
 * @license Copyright (c) 2003-2018, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	config.resize_minWidth = 450;
	// Define changes to default configuration here.
	// For complete reference see:
	// https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_config.html

	// The toolbar groups arrangement, optimized for a single toolbar row.
	config.toolbarGroups = [
		{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
		{ name: 'forms' },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph',   groups: [ 'list', 'blocks', 'align', 'bidi' ] },
		'/',
		{ name: 'links' },
		{ name: 'insert' },
		{ name: 'styles' },
		{ name: 'colors' },
		{ name: 'tools' },
		{ name: 'others' }
	];

	// The default plugins included in the basic setup define some buttons that
	// are not needed in a basic editor. They are removed here.
	config.removeButtons = 'Undo,Redo,Subscript,Superscript';
	// Set the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';

	// Dialog windows are also simplified.
	config.removeDialogTabs = 'link:advanced';
	var relativeurl=path;
	config.filebrowserBrowseUrl = relativeurl+'kcfinder/browse.php?opener=ckeditor&type=files';
	config.filebrowserImageBrowseUrl = relativeurl+'kcfinder/browse.php?opener=ckeditor&type=images';
	config.filebrowserFlashBrowseUrl = relativeurl+'kcfinder/browse.php?opener=ckeditor&type=flash';
	config.filebrowserUploadUrl = relativeurl+'kcfinder/upload.php?opener=ckeditor&type=files';
	config.filebrowserImageUploadUrl = relativeurl+'kcfinder/upload.php?opener=ckeditor&type=images';
	config.filebrowserFlashUploadUrl = relativeurl+'kcfinder/upload.php?opener=ckeditor&type=flash';
	config.allowedContent = true;
    config.contentsCss = [
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css',
		'https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css',
		CKEDITOR.basePath + 'contents.css'
    ];   
};
