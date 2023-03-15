import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  NbButtonModule,
  NbCardModule,
  NbContextMenuModule,
  NbDialogModule,
  NbIconModule,
  NbLayoutModule,
  NbListModule,
  NbMenuModule,
  NbSelectModule,
  NbSidebarModule,
  NbSpinnerModule,
  NbTagModule,
  NbThemeModule,
  NbTooltipModule,
  NbTreeGridModule,
  NbUserModule,
} from '@nebular/theme';
import { NbEvaIconsModule } from '@nebular/eva-icons';
import { TimePastPipe } from 'ng-time-past-pipe';

import { PostsGridComponent } from './posts-grid/posts-grid.component';
import { PostDetailComponent } from './post-detail/post-detail.component';
import { ProfileInfoComponent } from './profile-info/profile-info.component';
import { TaskStatusIconComponent } from './tasks/task-status-icon.component';
import { TaskTypeIconComponent } from './tasks/task-type-icon.component';

@NgModule({
  declarations: [
    AppComponent,
    PostsGridComponent,
    PostDetailComponent,
    ProfileInfoComponent,
    TaskStatusIconComponent,
    TaskTypeIconComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    NbButtonModule,
    NbCardModule,
    NbContextMenuModule,
    NbDialogModule.forRoot(),
    NbIconModule,
    NbLayoutModule,
    NbListModule,
    NbMenuModule.forRoot(),
    NbSelectModule,
    NbSidebarModule.forRoot(),
    NbSpinnerModule,
    NbTagModule,
    NbThemeModule.forRoot({ name: window.matchMedia("(prefers-color-scheme: dark)").matches ? 'dark' : 'default' }),
    NbTooltipModule,
    NbTreeGridModule,
    NbUserModule,
    NbEvaIconsModule,
    TimePastPipe,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
