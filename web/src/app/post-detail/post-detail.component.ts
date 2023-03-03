import { Component, Input, TemplateRef } from '@angular/core';

import { NbDialogService, NbDialogRef } from '@nebular/theme';

import { Post, PostService } from '../services/post.service';

@Component({
  selector: 'post-detail',
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss']
})
export class PostDetailComponent {
  @Input() post?: Post
  postService: PostService

  constructor(postService: PostService, private dialogService: NbDialogService) {
    this.postService = postService
  }

  showDeletePostConfirmation(dialog: TemplateRef<any>, shortcode: string) {
    this.dialogService.open(dialog, { hasScroll: true, context: {shortcode: shortcode} });
  }

  deletePost(dialogRef: NbDialogRef<TemplateRef<any>>, shortcode: string) {
    this.postService.deletePost(shortcode)
    dialogRef.close()
  }

  showDeleteItemConfirmation(dialog: TemplateRef<any>, shortcode: string, itemIndex: number) {
    this.dialogService.open(dialog, { hasScroll: true, context: {shortcode: shortcode, itemIndex: itemIndex} });
  }

  deleteItem(dialogRef: NbDialogRef<TemplateRef<any>>, shortcode: string, itemIndex: number) {
    this.postService.deleteItem(shortcode, itemIndex)
    dialogRef.close()
  }
}
